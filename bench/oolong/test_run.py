import importlib.util
import os
import secrets
import stat
import sys
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("azdaja_oolong_run",HERE/"run.py")
RUN=importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name]=RUN
assert SPEC.loader is not None
SPEC.loader.exec_module(RUN)


class ControllerTests(unittest.TestCase):
    def test_fixture_integrity_prompt_and_strict_score(self):
        fixture=RUN.load_fixture(str(HERE/"row-645.json"),None)
        self.assertEqual(fixture.expected_canonical,"Answer: 132")
        self.assertEqual(fixture.context_sha256,"05e4419a7280c91b3bbf1ea97629bfc235ee0eb23e67e1f0eeb21fc38b485bf2")
        prompt=RUN.build_prompt(fixture)
        self.assertIn("do not access the network",prompt)
        self.assertNotIn(fixture.expected_canonical,prompt)
        self.assertTrue(RUN.strict_score("Answer: 132",fixture)["correct"])
        self.assertFalse(RUN.strict_score("Answer: 132\nextra",fixture)["correct"])

    def test_gold_parser_rejects_free_text(self):
        self.assertEqual(RUN.parse_gold("['ham']","which label?"),("Label","ham","Label: ham"))
        with self.assertRaises(RUN.BenchError):
            RUN.parse_gold("Answer: 132","how many?")

    @unittest.skipUnless(hasattr(os,"getuid"),"Unix-only private runtime")
    def test_cleanup_accepts_only_owned_short_runtime(self):
        uid=os.getuid();root=Path(tempfile.mkdtemp(prefix="azdaja-cleanup-test-"));errors=[]
        try:
            private=root/"azdaja-state"/"jcode-api";private.mkdir(parents=True,mode=0o700)
            runtime=Path("/tmp")/f"azdaja-{uid}"/f"r-{secrets.token_hex(8)}"
            runtime.mkdir(parents=True,mode=0o700);os.chmod(runtime.parent,0o700);os.chmod(runtime,0o700)
            (private/"runtime-dir").write_text(str(runtime),encoding="utf-8")
            RUN.cleanup_private_azdaja_daemon(root,errors)
            self.assertEqual(errors,[]);self.assertFalse(runtime.exists())
            victim=root/"must-survive";victim.mkdir();(private/"runtime-dir").write_text(str(victim),encoding="utf-8")
            RUN.cleanup_private_azdaja_daemon(root,errors)
            self.assertTrue(victim.exists());self.assertTrue(errors)
        finally:
            import shutil
            shutil.rmtree(root,ignore_errors=True)

    def test_private_artifact_is_owner_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"trace"
            meta=RUN.write_private_artifact(path,"private trajectory")
            self.assertEqual(meta["sha256"],RUN.sha256_path(path))
            if os.name=="posix":self.assertEqual(stat.S_IMODE(path.stat().st_mode),0o600)


if __name__=="__main__":unittest.main()
