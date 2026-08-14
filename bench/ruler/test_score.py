from __future__ import annotations

import base64
import copy
import hashlib
import importlib.util
import itertools
import json
import os
import stat
import sys
import tempfile
import unittest
import zlib
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("azdaja_ruler_score", HERE / "score.py")
SCORE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = SCORE
assert SPEC.loader is not None
SPEC.loader.exec_module(SCORE)

RULER_LICENSE_BYTES = zlib.decompress(base64.b85decode(
    b"c-q}sTa(+i6@K@xKsD3p?hGwEY0@^%lj2=BY8~y)YF#&z$pb`!5^9oQ0CKhJukX3wMoGJNr*HLm5=$Zu4$kE}-#MTVpZT-sWw}%0"
    b"y)ISf)Qe}H{D-"
    b"nmn@)T^e_e>b$!?VPAijS6`kN;g?S`R$^Xk=pzn@FmW^U~ERl{4kS1)kk{q@~XYq3~eiMKbatL6RjX0;aYZtlc~^>rccu5a&du0F"
    b"iQuM2wWYPr6@TmJ9?zaar%&Bc|fb*BeV&dpzVZD#&NGvRi!X+*1JCk8m_pls`e>?%>3uHsdqHdc&I6~e0CnrbZZ>%xn|XDjUnt2Z"
    b"NlFQgL{ZmBA<If%6?S;$u)-"
    b"<ol|6W<9_!v_t|nR0AZHyrC_?1^Hf=?_+KcY`qdPFVpe!9qP8gdB&RvHIV%pO<rP#julufK9hn!oqG#4|zLe3aG7Y#5IXNQDW@yf"
    b"TX<=vLq=%3orvb>%|y&z$>Vg<E_D<gEdVdq*dWVLrNET8vJ(bDp*#Uwl$rX<R27!J?vNxZ#Wn4j3qt#(e?%+CRsH)JosqlrOfCkP"
    b"F(0qUTXHr7T`V$UP2{w$Nw(GU_>dw>G+(N!atD(tY~E?w+fwy`?|5*dBqB`-zhpic%Sx_Bs;gvUSl+YlnV`-"
    b"kbB%t_b92>HCVG(wnWhv-"
    b"@g9+C2eQGJZ$(NXdK)CR!1Lzo2+s{B8c3m4vbK0aOFgLre|{b&t{y73s{T)va`$F>+lzC@}R2`Wm%EOhZmq8L0j!m5zxEU&QZWqo"
    b"N*G6TTVi44ZD?)f{<SAaisND)yi5}PQTV<@lUu#Ybp&#lay7#!MZD(kxT(eC^|EUMz<Pw2R}Mf4|@zRM;n4uDzJXYJrd-"
    b"_@B>B2|5|THOTU9#8kNDv&E{Va3a6^e?!e!HJI03cqqe4nAIqKWK<kho5EY%nCuImI`lj(8Yas=jhr|`r19}-p$Aq-"
    b"$H71lH<@_<X5D9Pw_<C~S9KGPA4~*Up<#6t{s?t&nhdw{{M`J&ofWjWWB#jA&Fw#;A=q?;1CIFkxAFGuW0Lg>YjodUL|1(@F5KS="
    b"vOX)*NMqCK!24;YVBfPPt;9*T>mBWCwg)9`b^&&3d0P0b;J?sn%0oozVc_BWz=z9e_KSDA!W`CKiaHXt%04qKyfd+B2;|Rb#&fCD"
    b"B-b-"
    b"Q|1jRSfq4PRQ#R~Vp=!fWGtir9xU6>2|oi2A77=W_|r~#0fRy}BPB}Orr#^;GpU}0m!ClKM?oM)34hE+~Eh!nEEgw0GtNde3BR(G"
    b"(=sn1XGIN(%0N&i9|o6lPhquKk8#QUmYRV#JOPt{9Hk%D%iW3<Yu<^XxneImncAX+d^I@zkr;B*Z@WNTScktnhn8I5|P6k11_I(h"
    b"vqLb<Q;XFYzL12JW@{h|SV!i8EI^*~`0pHK`}o{0oWhHXQu;P<DLFS4W<5cLgg-"
    b"2~Wn;|8$9gGb;U6kVh_spnIHHX<B9p%uZ)RPLUw7CBKtRHp4Q-"
    b"Zu)2S%WE_CNE!B?ZqsfY35~dy^pXAi&O&%XbpgIfnM0ihT>>%aa~8`W9+>31!h5Rbd?N+b{bqt7P7x9o-"
    b"IWYyYfBYZ_)`6Q8&1_0ZIwdvXT|4kUO|RwJwKnsJWxU5>ir)^iQz+vGOrniCil;dXd4%BnmQXquqexmZPI8Pdm1Rm!3v`B*aUlNj"
    b"(N5OwStP5su<|U5;jSki4z5pAh<NVn=~;DW|s`VLyZ-`iKmBHWCr6W-"
    b"G9_6nU=BXQwHA#INJALk519^5h0Yd~A<46+2L7qadDuGAcrHP&(fyC81NljSxQ#Zd)3#H<xQ9yjl7&5Pdxte??k_+rEv*56nueM="
    b"q{DR?jvwS(@djte{GY%s>Jm1au}AN4x;YA)FEzUatnQOb9=KzNXr1<QkpnUXte>oESg81lD7>*f^PkY=*<j+A8>@f!IBm5`p}rn*"
    b"06_Hw@httbiQrF^*4=F2Q*}ZeT4~5dyVuBm{c=26X09>*yO#Eb_iBr}+_!i7cP&c&3~awy=Z#m^tWHBIy1fc;^C^seZr&gO+0m6b"
    b"Te`+z?%gp3j<j59m4w+sOw-EH5ZTeYB}-"
    b"<atm8R0HtK{{=)bc3{Uu9PmWhvqFNIa56Lj`zY)x`@X?;({$i;vNB?qSFLQM27B|f+2O#7BqX<P#LW(}*Ewl5WoK;xeL_d0bf|rK"
    b";$OH+XoF3sd_@HK14a^AJuN$45Dvs0uCKPBK9jtua(;_Fx+2uNxmecd|JVyTKq`#s=#)WkSp~V3_%nf=Z`?0Z!HV448s}b;!SEQR"
    b"8IeEnXYjlfjoiCY4|vo@ZMg`5#e(vQ6C9!9a{xy*ffaYY)lPEC<eWn|R`5qlOclg16`Mw4piH3|^_dbHjg(`)<ONp6)d5o!y%%Cd"
    b"x<J?}_%Z}vv@S@)KCxmb_+~EdR6ZG+)7Gs#BxE~AA;3W$xXlEQo?&_95~Pi=*$5y<afFNp{%>MMp0>?g!k<90BDF$fkQ7?2Qtaj0"
    b"G|&@qeGl06=0)tQF8QP*MA{bhMfJGf0Jmy5B7#;<ePefse@+f6sXiQc65mr94SQ~~J$Z1Gs5JIb*uV2o$6^RU`=C3F6Yd^ewmm{z"
    b"3~7{!t^1aYp;*pz=Q7*bssR$L2)sFK;i)?SjgAkOZ5%gD0a0LvrRrGt=q?ZzD}}tN$jAhR=#bLQpN&TlXY@IS)G2dg^b9gcxylfs"
    b"g(`!`M00Y+*&!9Kz~GM$IyG8#iJ%qz?;AgK^=x%>zkGW=gXDW0$ljQCeh;MF**<x8We{*CQ%)>P{>ns!)>DEHWko$^3OaSxtO!aH"
    b"=e(I14{C%Ad=NT9@g;W6#GJSAS-VoOfs95;hwW58rT0rxwgNGNP2U7HWzaF%I$3BERqk0GzR$sY5@dN^PX|y!*9m8^WNuRhJe6;3"
    b"acX55xL!8p^1Z<sE7eDtLIeUjKz0@gwAD*I<RSW|!}%OE%t$PhgeLTU$6XlW*QuE^e-"
    b"nA&Ryq#(pod7!D>9U+IzG1uu?~~jd@LKXs_@?y`<*-"
    b"@GburJZ=o;Ago3T_z!CYGsGq{|Mpdb<8rwiyClM2Xh5NtY&SOj?1BW37nBi<P(X<MBCguTlJdQs$%v1LkXHAs43ZktvtY-pnH2BI"
    b"~fkON_a+Pr;r;)WzSne4HpGJFUu8derc2{KTGujj>ZE9*34^Olr`E)L(63N4@vuR#Z;N-SyQiUVy##u5^X^f-"
    b"ESSEHVN1edLA>UH7<8K1ES4}L?&Bccfs;DEUsYlqT)Y$%##O#73&NmLnEHWErWn-)-"
    b"M^}mI<BrFJ9Hx4keER&~v}T@Wk(yb+un4BERk(fR^(!;rqIi2l^<`tYDZ{kgQhSGGgj91Qlmn+K#TP-"
    b"C2ANCzM$9gFKnhljEzuTwItu)Q&k*X!)T1ghh$rBU2C-"
    b"@@E#E60_a6Q(;7<UBfq*!K#f(Q+hLCe$%AMT^q2c|78q=3>jUii{n?**0Q!iy7aHj7+f=)h$`QZ?>LE|D#oqU^W)o-"
    b"Krw?|me9ry%GI=K`IziIJ$8npo{1Meu|fZi3c>A*?t$$U0sQ}COw24_kDTk6kqaitx#PIzfsi;uuR!7hiG1X0z^fg4!rys^bfFhE"
    b"|U<|R$RisUe#`!1<^fx6<*;J8K2pT_a!#JQI^*8<3&E!JYWo{1k8>*YEa_v7;Z$D0rL;^X4(Zn3&wUa!T?U4AWp^G+;QKa0OFS64"
    b"uHG~WO};&jxdlW4+~DjSog45B%y3^;XwCYMY_4Us*CSTN@O^8WpG0ajnVT&~{TEmwcN{^@#kUx=Ts@813hS}uNAzF*$|Od<4cdB3"
    b"_|^Xmf(FXMJ`2M+u2esL#mKiu8ktgpG+@@-**Hw&PD51VSbb)cIW?h2>j0-"
    b"m#`w;Jg=9k_<*!bd3n65?j_Ql2(C2b>6x8{k?yLUw0L9ou9Eb$`!F)7bo?^|YDg*!#;IJ_nQHqW4;EbVHZtORT&C=ubD09xMaCYG"
    b"~LAIzp$NjatG@76j0cj|@7sZ8Wg2Qe77Dw!4^&a^vLZv+;hxL;+{|jouKUBjvU@kBIjcVaoyEKyY+Bem*}KJtyS@hcdxsji!zLM1"
    b"Wi?Te+Ri@Nso`B_O>V;Ch93>)GuyBoq)^zDhs>!!upHkn=(VLgUO0^u}?u<vVk%;;~lat?_ZAOV%7C#*F-"
    b"p?z}TIT+Js27th{_2d(hfjp2aZ8dL3clg|!6K~Xk+FL6qUoM1%7YpI*jay61oJ$8xQP!T-yCJ5dFVDRSl;Ek1oz`-~~f_^-"
    b"R^D^QvT~-g8E=g<u`UYfxH$r&1!Hee%_--y1CDsJALO@>Jd65crmJ}a%NZqIDdVE><>~&jUq2<mPo`TY(b8^{EGgshkwIVzLs3Q$"
    b"!S1LY4&tp)Jeg}#>)pq!5Ng9Z;S(~7{Fq_6tp@_G<LfAp(%U3OM9?TctUuieF?tup5N3+LHh+D~MFtTSRIGvB)Xz7~lHY9Rxe=R~"
    b"oT>mu!X@XJGmzYkvMM;RBCPi5o_?a;FOuA-"
    b"##)Rj5C)?D~HkGQOUEvkLjH@%Fb7@;bqCl>r6;nEo)~4GsKRE_WhOQi&RUV=ir*q@Y!IO=2paWVU*))>*eHM)wZH&5b0AH`Ju&$n"
    b"a4UT?a+}^??%YVK>7t*u<5cS|+U&vqG!{11ieY{J;*XzD;LE&Gcm`)P{tu~M~7TWM3Of`zs$=6ynl@m}PAlVu8H+V~_ATnpa{5nf"
    b"b3Qi_`wL64hB2@KVU)D*_#l@BB{t(|6$Z|9Y|J|jaZk^gx2lN6W0Vsad!*>T++0O1}F<0CH@cc1egi=$_3II;P!p7kR6+i9gqyfe"
    b"0S&kcsGGwgWb`j0&Lop6ls~eSGS)m)!poznUGf<8O*NDM0tQFInPyg}@stJLo<9)ohT)20Q<C!$%kha|6jWq{Dx=j4#0DpcJzmVR"
    b"b=g}?euk^SNk}B(&rr}fMFNBH<d?3DadHFqx2>l2G0hcd7J`XfrcfJiJXp9jRDNfe)n+;9N<YZ(Q0$C0r+&}lq>3iVrtM&CuP??r"
    b"|2}6I1d-!+GUgT5CiM@h)_zFYzz*7wTf27}mc$3-IN=;M<K~A&=Vg`=ZZAS<=paf7By5l$d{In$Tb$5EM`F{YB=j>b"
))


def private_json(path: Path, value: object) -> None:
    path.write_bytes(SCORE.canonical_json_file_bytes(value))
    path.chmod(0o600)


def private_text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8")
    path.chmod(0o600)


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def base26(value: int, width: int, upper: bool = False) -> str:
    chars = []
    for _ in range(width):
        chars.append(chr((65 if upper else 97) + value % 26))
        value //= 26
    return "".join(reversed(chars))


class ScoreTests(unittest.TestCase):
    def make_artifacts(
        self, root: Path, *, failed_job: int | None = None,
        failed_jobs: set[int] | None = None,
        candidate_executable_match: bool = True,
    ):
        failed_ordinals = set(failed_jobs or ())
        if failed_job is not None:
            failed_ordinals.add(failed_job)
        root = root.resolve()
        root.chmod(0o700)
        master_key = bytes(range(32))
        plan_cells = []
        pool_rows_by_cell = {}
        for target_length in SCORE.TARGET_LENGTHS:
            for task in SCORE.TASKS:
                seed = int.from_bytes(
                    SCORE._derive(
                        master_key, SCORE.SUITE_ID, "generator", task, target_length
                    )[:4],
                    "big",
                )
                plan_cells.append(
                    {
                        "task": task,
                        "target_length": target_length,
                        "generator_seed": seed,
                    }
                )
                rows = []
                for pool_ordinal in range(100):
                    rows.append(
                        {
                            "ordinal": pool_ordinal,
                            "raw_row_sha256": sha(
                                f"pool-raw-{task}-{target_length}-{pool_ordinal}"
                            ),
                            "canonical_row_sha256": sha(
                                f"pool-canonical-{task}-{target_length}-{pool_ordinal}"
                            ),
                            "payload_sha256": sha(
                                f"pool-payload-{task}-{target_length}-{pool_ordinal}"
                            ),
                            "construction_tokens": 100 + pool_ordinal,
                            "row_length": 100 + pool_ordinal + SCORE.TASK_RESERVES[task],
                            **(
                                {"token_position_answer": pool_ordinal}
                                if task == "niah_multikey_3" else {}
                            ),
                        }
                    )
                pool_rows_by_cell[(task, target_length)] = rows
        plan = {
            "schema_version": 1,
            "record_type": "ruler_exact_mini_generation_plan",
            "suite_id": SCORE.SUITE_ID,
            "master_key_hex": master_key.hex(),
            "cells": plan_cells,
        }
        suite_root = root / "public"
        suite_root.mkdir(mode=0o700)
        license_path = suite_root / "LICENSE.NVIDIA-RULER"
        license_path.write_bytes(RULER_LICENSE_BYTES)
        license_path.chmod(0o600)
        notice_path = suite_root / "THIRD_PARTY_NOTICES.md"
        notice_path.write_bytes((HERE / "THIRD_PARTY_NOTICES.md").read_bytes())
        notice_path.chmod(0o600)
        self.assertEqual(
            SCORE.sha256_path(license_path),
            SCORE.EXPECTED_REDISTRIBUTION_FILES[license_path.name],
        )
        self.assertEqual(
            SCORE.sha256_path(notice_path),
            SCORE.EXPECTED_REDISTRIBUTION_FILES[notice_path.name],
        )
        payload_dir = suite_root / "payloads"
        payload_dir.mkdir(mode=0o700)
        fixtures = []
        gold_fixtures = []
        outputs_by_id = {}
        ordinal = 0
        for task in SCORE.TASKS:
            for target_length in SCORE.TARGET_LENGTHS:
                seed = next(
                    item["generator_seed"] for item in plan_cells
                    if item["task"] == task and item["target_length"] == target_length
                )
                rows = pool_rows_by_cell[(task, target_length)]
                selected = SCORE._select_pool_rows(rows, task, target_length, master_key)
                for pool_row, selection in selected:
                    fixture_id = SCORE._fixture_id(
                        master_key, task, target_length, pool_row
                    )
                    payload = payload_dir / f"{fixture_id}.txt"
                    if task == "niah_multikey_3":
                        outputs = [f"00000000-0000-4000-8000-{ordinal:012x}"]
                        query = f"11111111-1111-4111-8111-{ordinal:012x}"
                        input_text = (
                            "A special magic uuid is hidden within the following text. "
                            "Make sure to memorize it. I will quiz you about the uuid afterwards.\n"
                            f"The lookup key is {query}. The hidden value is {outputs[0]}."
                            f"\nWhat is the special magic uuid for {query} mentioned in the provided text?"
                        )
                        answer_prefix = (
                            f" The special magic uuid for {query} mentioned in the provided text is"
                        )
                    elif task == "vt":
                        outputs = [
                            base26(ordinal * 8 + offset, 5, upper=True)
                            for offset in range(5)
                        ]
                        query = f"{ordinal:05d}"
                        assignments = " ".join(f"{value} = {query}." for value in outputs)
                        input_text = (
                            "Memorize and track the chain(s) of variable assignment hidden in the following text.\n\n"
                            + assignments
                            + f"\nQuestion: Find all variables that are assigned the value {query} in the text above."
                        )
                        answer_prefix = (
                            " Answer: According to the chain(s) of variable assignment in the text above, "
                            f"5 variables are assigned the value {query}, they are: "
                        )
                    else:
                        outputs = [base26(ordinal * 4 + offset, 6) for offset in range(3)]
                        context = " ".join(
                            [outputs[0]] * 4 + [outputs[1]] * 3 + [outputs[2]] * 2 + ["zzzzzz"]
                        )
                        input_text = (
                            "Read the following coded text and track the frequency of each coded word. "
                            "Find the three most frequently appeared coded words. "
                            + context
                            + "\nQuestion: Do not provide any explanation. Please ignore the dots '....'. "
                            "What are the three most frequently appeared words in the above coded text?"
                        )
                        answer_prefix = (
                            " Answer: According to the coded text above, the three most frequently appeared words are:"
                        )
                    private_text(payload, input_text + answer_prefix)
                    # The test payload hash is authoritative; reflect it in the
                    # selected pool receipt just as the real generator does.
                    pool_row["payload_sha256"] = SCORE.sha256_path(payload)
                    raw_row = {
                        "index": (
                            input_text.find(outputs[0])
                            if task == "niah_multikey_3" else pool_row["ordinal"]
                        ),
                        "input": input_text,
                        "outputs": outputs,
                        "length": pool_row["row_length"],
                        "length_w_model_temp": pool_row["row_length"],
                        "answer_prefix": answer_prefix,
                        **(
                            {"token_position_answer": pool_row["token_position_answer"]}
                            if task == "niah_multikey_3" else {}
                        ),
                    }
                    raw_row_utf8 = json.dumps(
                        raw_row, sort_keys=False, ensure_ascii=False, separators=(",", ":")
                    )
                    pool_row["raw_row_sha256"] = SCORE.sha256_bytes(raw_row_utf8.encode("utf-8"))
                    pool_row["canonical_row_sha256"] = SCORE.sha256_bytes(
                        SCORE.canonical_json_file_bytes(raw_row)
                    )
                    fixture_id = SCORE._fixture_id(
                        master_key, task, target_length, pool_row
                    )
                    renamed_payload = payload_dir / f"{fixture_id}.txt"
                    payload.rename(renamed_payload)
                    payload = renamed_payload
                    outputs_by_id[fixture_id] = outputs
                    fixtures.append(
                        {
                            "id": fixture_id,
                            "task": task,
                            "target_length": target_length,
                            "payload": f"payloads/{payload.name}",
                            "payload_sha256": pool_row["payload_sha256"],
                            "payload_bytes": payload.stat().st_size,
                            "construction_tokens": pool_row["construction_tokens"],
                            "row_length": pool_row["row_length"],
                        }
                    )
                    gold_fixtures.append(
                        {
                            "id": fixture_id,
                            "task": task,
                            "target_length": target_length,
                            "outputs": outputs,
                            "raw_row_sha256": pool_row["raw_row_sha256"],
                            "canonical_row_sha256": pool_row["canonical_row_sha256"],
                            "raw_row_utf8": raw_row_utf8,
                            "ordinal": pool_row["ordinal"],
                            "generator_seed": seed,
                            "payload_sha256": pool_row["payload_sha256"],
                            "selection": selection,
                        }
                    )
                    ordinal += 1

        plan_sha256 = SCORE.sha256_bytes(SCORE.canonical_json_file_bytes(plan))
        manifest = {
            "schema_version": 1,
            "record_type": "ruler_exact_mini_public_manifest",
            "suite_id": SCORE.SUITE_ID,
            "upstream_commit": SCORE.RULER_COMMIT,
            "source": {
                "name": "NVIDIA/RULER",
                "url": SCORE.RULER_URL,
                "commit": SCORE.RULER_COMMIT,
            },
            "configuration": {
                "tasks": list(SCORE.TASKS),
                "target_lengths": list(SCORE.TARGET_LENGTHS),
                "pool_size": 100,
                "per_cell": SCORE.EXPECTED_PER_CELL,
                "tokenizer": "cl100k_base",
                "task_generation_reserves": SCORE.TASK_RESERVES,
                "payload_rule": 'row["input"] + row["answer_prefix"]',
                "selection": {
                    "niah_multikey_3": "one secret-HMAC-ranked row per answer-position decile",
                    "vt": "ten secret-HMAC-ranked line ordinals",
                    "fwe": "ten secret-HMAC-ranked line ordinals",
                },
            },
            "provenance_commitments": {
                "generation_plan_sha256": plan_sha256,
                "requirements_lock_sha256": SCORE.REQUIREMENTS_LOCK_SHA256,
                "tokenizer_blob_sha256": SCORE.TOKENIZER_BLOB_SHA256,
                "ruler_source_files": SCORE.EXPECTED_RULER_SOURCE_HASHES,
            },
            "redistribution_files": SCORE.EXPECTED_REDISTRIBUTION_FILES,
            "fixtures": fixtures,
        }
        identity_sha = SCORE.sha256_bytes(SCORE.canonical_json_file_bytes(manifest))
        pool_receipts = []
        for task in SCORE.TASKS:
            for target_length in SCORE.TARGET_LENGTHS:
                seed = next(
                    item["generator_seed"] for item in plan_cells
                    if item["task"] == task and item["target_length"] == target_length
                )
                pool_receipts.append(
                    {
                        "task": task,
                        "target_length": target_length,
                        "generator_seed": seed,
                        "generation_cwd": "/RULER/scripts/data",
                        "generation_argv": [
                            "/private/tmp/venv/bin/python", "-I", "-S", "-B", "-c",
                            SCORE.ISOLATED_GENERATION_BOOTSTRAP,
                            "/RUNTIME/site-packages",
                            "/RULER/scripts/data/prepare.py",
                            "--save_dir", f"/POOL/{target_length}",
                            "--benchmark", "synthetic", "--task", task,
                            "--subset", "test", "--tokenizer_path", "cl100k_base",
                            "--tokenizer_type", "openai", "--max_seq_length", str(target_length),
                            "--model_template_type", "base", "--num_samples", "100",
                            "--random_seed", str(seed),
                        ],
                        "rows": pool_rows_by_cell[(task, target_length)],
                    }
                )
        gold = {
            "schema_version": 1,
            "record_type": "ruler_exact_mini_gold",
            "suite_id": SCORE.SUITE_ID,
            "manifest_identity_sha256": identity_sha,
            "provenance": {
                "generation_plan": plan,
                "generation_plan_sha256": plan_sha256,
                "upstream": {
                    "url": SCORE.RULER_URL,
                    "commit": SCORE.RULER_COMMIT,
                    "files": SCORE.EXPECTED_RULER_SOURCE_HASHES,
                },
                "dependencies": {
                    "requirements_lock_sha256": SCORE.REQUIREMENTS_LOCK_SHA256,
                    "python": {
                        "implementation": "CPython", "version": "3.11.13",
                        "executable": "/private/tmp/venv/bin/python",
                        "build": ["main", "Aug 1 2026"],
                    },
                    "platform": {
                        "description": "test-platform", "os": "Darwin",
                        "release": "test", "machine": "arm64",
                    },
                    "packages": SCORE.EXPECTED_PACKAGE_VERSIONS,
                    "wheels": {
                        name: {"filename": f"{name}-test.whl", "sha256": "d" * 64}
                        for name in SCORE.EXPECTED_PACKAGE_VERSIONS
                    },
                    "site_packages_sha256": "e" * 64,
                    "tokenizer": {
                        "name": "cl100k_base",
                        "blob_sha256": SCORE.TOKENIZER_BLOB_SHA256,
                        "cache_filename": SCORE.TOKENIZER_CACHE_NAME,
                    },
                    "nltk_resources": SCORE.EXPECTED_NLTK_RESOURCE_HASHES,
                },
                "pool_receipts": pool_receipts,
            },
            "fixtures": gold_fixtures,
        }
        gold_path = root / "gold.json"
        private_json(gold_path, gold)
        manifest["gold_sha256"] = SCORE.sha256_path(gold_path)
        manifest_path = suite_root / "manifest.json"
        private_json(manifest_path, manifest)

        identity_root = root / "identity"
        identity_root.mkdir(mode=0o700)
        candidate_snapshot_root = identity_root / "candidate"
        controller_snapshot_root = identity_root / "controller"
        executable_snapshot_root = identity_root / "executables"
        candidate_snapshot_root.mkdir(mode=0o700)
        controller_snapshot_root.mkdir(mode=0o700)
        executable_snapshot_root.mkdir(mode=0o700)
        candidate_paths = {
            name: candidate_snapshot_root / name
            for name in ("azdaja", "config.toml", "SKILL.md")
        }
        for name, path in candidate_paths.items():
            content = (
                'default_model="gpt-5.6-luna"\n'
                'jcode_repair_model="gpt-5.6-luna"\n'
                if name == "config.toml"
                else f"test candidate {name}"
            )
            private_text(path, content)
            path.chmod(0o500 if name == "azdaja" else 0o400)
        candidate_components = {
            name: {
                "path": str(path), "sha256": SCORE.sha256_path(path),
                "bytes": path.stat().st_size,
                "mode": "0500" if name == "azdaja" else "0400",
            }
            for name, path in candidate_paths.items()
        }
        candidate_bound = {
            name: {
                "sha256": item["sha256"], "bytes": item["bytes"],
                "mode": item["mode"],
            }
            for name, item in sorted(candidate_components.items())
        }
        candidate = {
            "sha256": SCORE.sha256_bytes(
                SCORE.canonical_json_bytes(candidate_bound)
            ),
            "snapshot_root": str(candidate_snapshot_root),
            "components": candidate_components,
        }
        controller_paths = {
            "ruler_runner": controller_snapshot_root / "ruler_runner.py",
            "oolong_execution_module": controller_snapshot_root / "oolong_execution_module.py",
        }
        private_text(controller_paths["ruler_runner"], "test runner")
        private_text(controller_paths["oolong_execution_module"], "test oolong")
        for path in controller_paths.values():
            path.chmod(0o500)
        controller_components = {
            name: {
                "path": str(path), "sha256": SCORE.sha256_path(path),
                "bytes": path.stat().st_size,
            }
            for name, path in controller_paths.items()
        }
        controller_bound = {
            name: {"sha256": item["sha256"], "bytes": item["bytes"]}
            for name, item in sorted(controller_components.items())
        }
        controller = {
            "sha256": SCORE.sha256_bytes(SCORE.canonical_json_bytes(controller_bound)),
            "components": controller_components,
        }

        prime_bundle_root = executable_snapshot_root / "prime-agent-package"
        prime_entrypoint = prime_bundle_root / "dist" / "bundle" / "cli.js"
        prime_entrypoint.parent.mkdir(mode=0o700, parents=True)
        for directory in (prime_bundle_root, prime_bundle_root / "dist", prime_entrypoint.parent):
            directory.chmod(0o700)
        private_text(prime_entrypoint, "prime-agent")
        prime_entrypoint.chmod(0o500)
        prime_files = [
            {
                "relative_path": "dist", "kind": "directory",
                "sha256": None, "bytes": 0, "mode": "0700",
            },
            {
                "relative_path": "dist/bundle", "kind": "directory",
                "sha256": None, "bytes": 0, "mode": "0700",
            },
            {
                "relative_path": "dist/bundle/cli.js", "kind": "file",
                "sha256": SCORE.sha256_path(prime_entrypoint),
                "bytes": prime_entrypoint.stat().st_size,
                "mode": "0500",
            },
        ]
        prime_bundle = {
            "root": str(prime_bundle_root),
            "entrypoint": "dist/bundle/cli.js",
            "aggregate_sha256": SCORE.sha256_bytes(
                SCORE.canonical_json_bytes(prime_files)
            ),
            "files": prime_files,
        }
        executable_paths = {
            "jcode": executable_snapshot_root / "jcode-test",
            "azdaja": executable_snapshot_root / "azdaja-test",
            "prime-agent": prime_entrypoint,
        }
        for executable_name in ("jcode", "azdaja"):
            executable_path = executable_paths[executable_name]
            if executable_name == "azdaja":
                executable_path.write_bytes(
                    candidate_paths["azdaja"].read_bytes()
                    if candidate_executable_match else b"mismatched candidate executable"
                )
                executable_path.chmod(0o600)
            else:
                private_text(executable_path, executable_name)
            executable_path.chmod(0o500)

        source_candidate = root / "source-candidate"
        source_candidate.mkdir(mode=0o700)
        private_text(source_candidate / "ignored-extra.txt", "not staged")

        schedule = {
            "schema_version": 1,
            "record_type": "ruler_frozen_schedule",
            "suite": {
                "suite_id": SCORE.SUITE_ID,
                "manifest_sha256": SCORE.sha256_path(manifest_path),
                "fixtures": [
                    {
                        "fixture_id": fixture["id"],
                        "payload_sha256": fixture["payload_sha256"],
                        "task": fixture["task"],
                        "target_length": fixture["target_length"],
                        "staged_filename": f"{fixtures.index(fixture):032x}.txt",
                    }
                    for fixture in fixtures
                ],
            },
            "configuration": {
                "model": SCORE.MODEL,
                "reasoning": "medium",
                "arms": list(SCORE.ARMS),
                "repetitions": 1,
                "seed": 20260813,
                "timeout_seconds": 1800,
                "workflow": SCORE.FULL_WORKFLOW,
                "workflow_fixture_ids": None,
                "workflow_fixture_ids_sha256": None,
                "parallel_width": SCORE.PARALLEL_WIDTH,
                "configured_global_width": SCORE.PARALLEL_WIDTH,
                "parallel_width_scope": SCORE.PARALLEL_WIDTH_SCOPE,
                "wrapper_template_sha256": SCORE.WRAPPER_TEMPLATE_SHA256,
                "candidate": candidate,
                "candidate_source_path": str(source_candidate),
                "controller": controller,
                "controller_source_paths": {
                    "ruler_runner": str(controller_paths["ruler_runner"]),
                    "oolong_execution_module": str(controller_paths["oolong_execution_module"]),
                },
                "executables": {
                    name: {
                        "path": str(path), "sha256": SCORE.sha256_path(path),
                        "bytes": path.stat().st_size,
                        "version": f"{name} test",
                        "version_command": [str(path), "--version"],
                        "bundle": prime_bundle if name == "prime-agent" else None,
                        "smoke": (
                            {
                                "command": [str(path), "--version"],
                                "returncode": 0,
                                "stdout": f"{name} test\n",
                                "stderr": "",
                                "matched_source_version": True,
                            }
                            if name == "prime-agent" else None
                        ),
                    }
                    for name, path in executable_paths.items()
                },
                "containment": {
                    "os_level_asserted": False,
                    "disclaimer": "owner-only isolation and event auditing are advisory, not OS-level containment",
                    "claim_ledger": "local append-only creation protocol is not authenticated against malicious same-owner deletion/retry; external signing or transparency is future work",
                },
            },
            "jobs": [],
        }
        rng = __import__("random").Random(schedule["configuration"]["seed"])
        fixture_order = list(fixtures)
        rng.shuffle(fixture_order)
        workflow_fixture_ids = [fixture["id"] for fixture in fixture_order]
        schedule["configuration"]["workflow_fixture_ids"] = workflow_fixture_ids
        schedule["configuration"]["workflow_fixture_ids_sha256"] = SCORE.sha256_bytes(
            SCORE.canonical_json_bytes(workflow_fixture_ids)
        )
        permutations = list(itertools.permutations(SCORE.ARMS)) * 15
        rng.shuffle(permutations)
        job_ordinal = 0
        for fixture, order in zip(fixture_order, permutations):
            fixture_index = fixtures.index(fixture)
            for arm in order:
                job_ordinal += 1
                schedule["jobs"].append(
                    {
                        "ordinal": job_ordinal,
                        "fixture_id": fixture["id"],
                        "payload_sha256": fixture["payload_sha256"],
                        "task": fixture["task"],
                        "target_length": fixture["target_length"],
                        "staged_filename": f"{fixture_index:032x}.txt",
                        "repetition": 1,
                        "arm": arm,
                    }
                )
        schedule_id = SCORE.sha256_bytes(SCORE.canonical_json_bytes(schedule))
        for job in schedule["jobs"]:
            job["run_id"] = SCORE.sha256_bytes(
                SCORE.RUN_ID_DOMAIN
                + schedule_id.encode("ascii")
                + SCORE.canonical_json_bytes(job)
            )
        schedule["schedule_id"] = schedule_id
        runs_path = root / "runs.jsonl"
        schedule_path = Path(str(runs_path) + ".schedule.json")
        private_json(schedule_path, schedule)

        rows = []
        artifacts_root = root / "artifacts"
        artifacts_root.mkdir(mode=0o700)
        for job in schedule["jobs"]:
            expected = outputs_by_id[job["fixture_id"]]
            artifact_dir = artifacts_root / (
                f"{job['ordinal']:03d}-{job['run_id'][:16]}-{job['arm']}"
            )
            artifact_dir.mkdir(mode=0o700)
            stdout_path = artifact_dir / "stdout.ndjson"
            stderr_path = artifact_dir / "stderr.log"
            execution_success = job["ordinal"] not in failed_ordinals
            if job["arm"] == "prime-agent":
                stdout_evidence = json.dumps({
                    "type": "message_end",
                    "message": {
                        "role": "assistant", "provider": "openai-codex",
                        "model": SCORE.MODEL, "api": "openai-codex-responses",
                        "usage": {
                            "input": 100, "output": 5, "cacheRead": 20,
                            "cacheWrite": 0, "totalTokens": 125,
                        },
                    },
                })
            elif job["arm"] == "jcode-native":
                stdout_evidence = "\n".join((
                    json.dumps({
                        "type": "tokens", "input": 100, "output": 5,
                        "cache_read_input": 20, "cache_creation_input": 0,
                    }),
                    json.dumps({"type": "done", "provider": "OpenAI", "model": SCORE.MODEL}),
                ))
            else:
                request_id = f"1-{job['ordinal']}-1"
                stdout_evidence = json.dumps({
                    "schema_version": 2, "event": "model_attempt",
                    "depth": 0, "request_id": request_id, "attempt": 1,
                    "entered_turn": 1, "session_id": None, "category": "turn",
                    "outcome": "succeeded", "input_tokens": 100,
                    "output_tokens": 5, "cache_read_tokens": 20,
                    "timestamp_ms": 1, "latency_ms": 1,
                    "provider": "OpenAI", "model": SCORE.MODEL,
                    "degraded_transport": False,
                    "failed_attempts_before_success": 0,
                })
            private_text(stdout_path, stdout_evidence)
            private_text(stderr_path, "test stderr")
            model_trace_path = artifact_dir / "azdaja-model-usage.jsonl"
            solo_trace_path = artifact_dir / "azdaja-solo-trace.log"
            runtime_row = None
            if job["arm"] == "jcode-azdaja":
                # The exact product footer is absolute EOF and request-bound.
                runtime_row = {
                    "schema_version": 1, "event": "solo_runtime",
                    "request_id": request_id,
                    "outcome": "succeeded" if execution_success else "failed",
                    "exec_invocation_count": 1 if execution_success else 0,
                    "exec_wall_ns": 1_000_000 if execution_success else 0,
                    "snapshot_save_count": 1 if execution_success else 0,
                    "snapshot_save_wall_ns": 100_000 if execution_success else 0,
                    "snapshot_load_count": 0, "snapshot_load_wall_ns": 0,
                    "sub_call_count": 0, "sub_call_wall_ns": 0,
                }
                solo_evidence = (
                    f'{{"event":"solo_started"}}\n'
                    f'=== solo runtime trace begin request_id="{request_id}" ===\n'
                    + json.dumps(runtime_row, separators=(",", ":"))
                    + f'\n=== solo runtime trace end request_id="{request_id}" ===\n'
                )
                private_text(solo_trace_path, solo_evidence)
                if execution_success:
                    private_text(model_trace_path, stdout_evidence)

            def artifact_record(path):
                return {
                    "path": str(path), "sha256": SCORE.sha256_path(path),
                    "bytes": path.stat().st_size, "mode": "0600",
                    "contains_private_raw_trajectory": False,
                    "credential_redacted": True, "sensitivity": "test evidence",
                }
            if job["arm"] == "jcode-native":
                response = "\n".join(f"{i}. {value}" for i, value in enumerate(expected, 1))
            elif job["arm"] == "jcode-azdaja":
                response = ", ".join(expected) + " -- explanation"
            else:
                response = ", ".join(expected[:-1]) or "missing"
            if job["arm"] == "jcode-azdaja" and execution_success:
                performance_ledger = {
                    "schema_version": 1, "complete": True,
                    "root_turn_count": 1, "root_inference_ms": 1,
                    "exec_invocation_count": 1, "exec_wall_ms": 1.0,
                    "snapshot_save_count": 1, "snapshot_save_ms": 0.1,
                    "snapshot_load_count": 0, "snapshot_load_ms": 0.0,
                    "sub_call_count": 0, "sub_call_turn_count": 0,
                    "sub_call_wall_ms": 0.0, "repair_count": 0,
                    "configured_global_width": SCORE.PARALLEL_WIDTH,
                    "parallel_width_scope": SCORE.PARALLEL_WIDTH_SCOPE,
                    "observed_active_at_start": min(job["ordinal"], SCORE.PARALLEL_WIDTH),
                    "repair_cost": {
                        "inference_ms": 0, "input_tokens": 0,
                        "output_tokens": 0, "cache_read_tokens": 0,
                        "token_accounting_complete": True,
                    },
                }
                performance_assertion = {
                    "applicable": True, "asserted": True,
                    "authority": SCORE.PERFORMANCE_AUTHORITY,
                    "raw_runtime": runtime_row, "reasons": [],
                }
            elif job["arm"] == "jcode-azdaja":
                performance_ledger = None
                performance_assertion = {
                    "applicable": True, "asserted": False,
                    "authority": SCORE.PERFORMANCE_AUTHORITY,
                    "raw_runtime": None,
                    "reasons": ["required model or solo trace path is unavailable"],
                }
            else:
                performance_ledger = None
                performance_assertion = {
                    "applicable": False, "asserted": True,
                    "authority": "not applicable to control arm",
                    "raw_runtime": None, "reasons": [],
                }
            row = {
                "schema_version": 1,

                "record_type": "inference",
                "schedule_id": schedule_id,
                "run_id": job["run_id"],
                "fixture_id": job["fixture_id"],
                "payload_sha256": job["payload_sha256"],
                "execution_ordinal": job["ordinal"],
                "arm": job["arm"],
                "repetition": 1,
                "model": SCORE.MODEL,
                "reasoning": "medium",
                "schedule_seed": schedule["configuration"]["seed"],
                "workflow": schedule["configuration"]["workflow"],
                "workflow_fixture_ids_sha256": schedule["configuration"][
                    "workflow_fixture_ids_sha256"
                ],
                "parallel_width": SCORE.PARALLEL_WIDTH,
                "configured_global_width": SCORE.PARALLEL_WIDTH,
                "parallel_width_scope": SCORE.PARALLEL_WIDTH_SCOPE,
                "candidate_sha256": candidate["sha256"],
                "controller_sha256": controller["sha256"],
                "timeout_seconds": 1800,
                "success": None,
                "score": None,
                "scoring_status": "deferred",
                "execution_success": execution_success,
                "latency_seconds": 1.5,
                "timed_out": not execution_success,
                "exit_code": 0 if execution_success else None,
                "failure": None if execution_success else {"kind": "timeout", "message": "timed out"},
                "route_assertion": {
                    "asserted": execution_success,
                    "subscription": execution_success,
                    "provider": "OpenAI OAuth" if job["arm"].startswith("jcode") else "openai-codex",
                    "model": SCORE.MODEL,
                },
                "lifecycle_assertion": {
                    "asserted": execution_success,
                    "isolated_home": execution_success,
                    "fresh_session": execution_success,
                    "cleanup_complete": execution_success,
                },
                "usage": {
                    "input_tokens": 100,
                    "output_tokens": 5,
                    "cache_read_tokens": 20,
                    "cache_write_tokens": 0,
                    "total_tokens": 125 if job["arm"] == "prime-agent" else 105,
                    "accounting_complete": True,
                } if execution_success else None,
                "arm_evidence": {
                    "staged_filename": job["staged_filename"],
                    "wrapper_sha256": SCORE.WRAPPER_TEMPLATE_SHA256,
                    "performance_ledger": performance_ledger,
                    "performance_ledger_assertion": performance_assertion,
                    "runner_parallelism": {
                        "schema_version": 1,
                        "configured_global_width": SCORE.PARALLEL_WIDTH,
                        "scope": SCORE.PARALLEL_WIDTH_SCOPE,
                        "observed_active_at_start": min(
                            job["ordinal"], SCORE.PARALLEL_WIDTH
                        ),
                        "observed_peak_concurrency": SCORE.PARALLEL_WIDTH,
                        "batch_started_at_unix_s": 1.0,
                        "monotonic_arm_start_offset_ms": float(job["ordinal"] - 1),
                        "monotonic_arm_end_offset_ms": float(job["ordinal"] + 3),
                        "controller_arm_wall_ms": 4.0,
                        "overall_makespan_ms": float(len(schedule["jobs"]) + 3),
                        "authority": SCORE.RUNNER_PARALLELISM_AUTHORITY,
                    },
                    "trajectory_artifacts": {
                        "stdout": artifact_record(stdout_path),
                        "stderr": artifact_record(stderr_path),
                        **(
                            {"azdaja_solo_trace": artifact_record(solo_trace_path)}
                            if job["arm"] == "jcode-azdaja" else {}
                        ),
                        **(
                            {"azdaja_model_trace": artifact_record(model_trace_path)}
                            if job["arm"] == "jcode-azdaja" and execution_success else {}
                        ),
                    },
                },
                "containment": {
                    "os_level_asserted": False,
                    "disclaimer": "advisory test isolation; no OS-level containment",
                    "claim_ledger": "local append-only creation protocol is not authenticated against malicious same-owner deletion/retry; external signing or transparency is future work",
                },
                "response": response,
            }
            rows.append(row)
        runs_path.write_bytes(b"".join(SCORE.canonical_json_file_bytes(row) for row in rows))
        runs_path.chmod(0o600)

        claims_root = Path(str(runs_path) + ".claims")
        claims_root.mkdir(mode=0o700)
        claims = claims_root / schedule_id
        claims.mkdir(mode=0o700)
        for row, job in zip(rows, schedule["jobs"]):
            private_json(
                claims / (job["run_id"] + ".json"),
                {
                    "schedule_id": schedule_id,
                    "run_id": job["run_id"],
                    "ordinal": job["ordinal"],
                    "pid": 123,
                },
            )
            private_json(
                claims / (job["run_id"] + ".done.json"),
                {
                    "schedule_id": schedule_id,
                    "run_id": job["run_id"],
                    "row_sha256": SCORE.sha256_bytes(SCORE.canonical_json_bytes(row)),
                },
            )
        return manifest_path, gold_path, runs_path, schedule_path, claims_root, schedule, rows

    def test_upstream_string_match_all_coverage_is_preserved(self):
        predictions = ["The answers are Alpha and BETA", "gamma only"]
        references = [["alpha", "beta"], ["gamma", "delta"]]
        self.assertEqual(SCORE.string_match_all(predictions, references), 75.0)
        self.assertEqual(SCORE.official_ruler_coverage(predictions[0], references[0]), 1.0)

    def test_exact_set_requires_each_value_once_and_only_formatting(self):
        refs = ["ALPHA", "BETA"]
        accepted = (
            "ALPHA, BETA",
            "beta\nALPHA",
            "1. alpha\n2) BETA",
            "[`Alpha`; (BETA)]",
        )
        for prediction in accepted:
            with self.subTest(prediction=prediction):
                self.assertTrue(SCORE.exact_set(prediction, refs))
        rejected = (
            "ALPHA",                         # missing
            "ALPHA BETA beta",               # duplicate
            "The answer is ALPHA, BETA",     # prose
            "ALPHA, BETA, GAMMA",            # foreign alphabetic value
            "ALPHA, BETA, 42",               # foreign bare number
            "ALPHA, BETA, 42.",              # not a line-leading list marker
            "ALPHA1. BETA2)",                 # answer-adjacent fake ordinals
            "1.ALPHA2)BETA",                  # only first is a valid list marker
            "ſALPHA, BETA",                   # Unicode case-fold is not ASCII match
            "KALPHA, BETA",                   # Unicode Kelvin fold is not ASCII match
            "ALPHA\n42.",                     # orphan ordinal line
            "42.\nALPHA, BETA",               # ordinal labels no answer on its line
            "ALPHA, BETA\x00",           # forged internal sentinel/control
            "ALPHA, BETA 😀",                 # foreign symbol
        )
        for prediction in rejected:
            with self.subTest(prediction=prediction):
                self.assertFalse(SCORE.exact_set(prediction, refs))

    def test_exact_unicode_root_leak_scan_has_no_normalization_or_match_text(self):
        payload = "left " + ("🦀Cafe\u0001" * 20) + " right"
        exact = ("🦀Cafe\u0001" * 20)[:100]
        transcript = "prefix" + exact + "suffix"
        self.assertTrue(SCORE.exact_unicode_substring_present(payload, transcript))
        self.assertFalse(
            SCORE.exact_unicode_substring_present(payload, transcript.replace("Cafe", "CAFÉ"))
        )
        audit = SCORE.root_context_leak_audit(
            payload.encode("utf-8"), transcript.encode("utf-8")
        )
        self.assertTrue(audit["detected"])
        self.assertEqual(audit["normalization"], "none")
        self.assertEqual(audit["exemptions"], "none")
        self.assertFalse(audit["matched_text_retained"])
        self.assertNotIn(exact, json.dumps(audit, ensure_ascii=False))

    def test_root_context_leak_false_success_is_rejected_before_gold(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, gold, runs, _, claims_root, schedule, rows = self.make_artifacts(root)
            row = next(
                item for item in rows
                if item["arm"] == "jcode-azdaja" and item["execution_success"]
            )
            manifest_doc = json.loads(manifest.read_text(encoding="utf-8"))
            fixture = next(
                item for item in manifest_doc["fixtures"]
                if item["id"] == row["fixture_id"]
            )
            payload = (manifest.parent / fixture["payload"]).read_text(encoding="utf-8")
            leaked = payload[:SCORE.ROOT_LEAK_MIN_CHARS]
            self.assertEqual(len(leaked), SCORE.ROOT_LEAK_MIN_CHARS)
            record = row["arm_evidence"]["trajectory_artifacts"]["azdaja_solo_trace"]
            trace_path = Path(record["path"])
            private_text(trace_path, "root request\n" + leaked + "\nroot response")
            record["sha256"] = SCORE.sha256_path(trace_path)
            record["bytes"] = trace_path.stat().st_size
            runs.write_bytes(b"".join(SCORE.canonical_json_file_bytes(item) for item in rows))
            runs.chmod(0o600)
            done = claims_root / schedule["schedule_id"] / (row["run_id"] + ".done.json")
            private_json(done, {
                "schedule_id": schedule["schedule_id"],
                "run_id": row["run_id"],
                "row_sha256": SCORE.sha256_bytes(SCORE.canonical_json_bytes(row)),
            })
            with mock.patch.object(SCORE, "load_gold", side_effect=AssertionError("gold read")):
                with self.assertRaisesRegex(SCORE.ScoreError, "falsely claims success.*root_context_leak"):
                    SCORE.build_report(manifest, gold, runs, bootstrap_resamples=1)

    def test_performance_ledger_is_independently_recomputed_and_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = self.make_artifacts(Path(directory))
            row = next(
                item for item in baseline[6]
                if item["arm"] == "jcode-azdaja" and item["execution_success"]
            )
            artifacts = row["arm_evidence"]["trajectory_artifacts"]
            retained = {
                name: Path(record["path"]).read_bytes()
                for name, record in artifacts.items()
            }
            audited = SCORE._audit_performance_evidence(row, retained, 1)
            self.assertEqual(audited, row["arm_evidence"]["performance_ledger"])

            tampered = copy.deepcopy(row)
            tampered["arm_evidence"]["performance_ledger"]["root_turn_count"] += 1
            with self.assertRaisesRegex(SCORE.ScoreError, "performance ledger"):
                SCORE._audit_performance_evidence(tampered, retained, 1)

            missing = copy.deepcopy(row)
            missing["arm_evidence"].pop("performance_ledger")
            with self.assertRaisesRegex(SCORE.ScoreError, "performance ledger"):
                SCORE._audit_performance_evidence(missing, retained, 1)

            trace_tampered = dict(retained)
            trace_tampered["azdaja_solo_trace"] += b"unexpected trailing row\n"
            with self.assertRaisesRegex(SCORE.ScoreError, "runtime footer"):
                SCORE._audit_performance_evidence(row, trace_tampered, 1)

    def test_failed_treatment_missing_solo_trace_blocks_gold(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = self.make_artifacts(Path(directory))
            failed_ordinal = next(
                row["execution_ordinal"] for row in baseline[6]
                if row["arm"] == "jcode-azdaja"
            )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, gold, runs, _, claims_root, schedule, rows = self.make_artifacts(
                root, failed_job=failed_ordinal
            )
            row = next(item for item in rows if item["execution_ordinal"] == failed_ordinal)
            self.assertEqual(row["arm"], "jcode-azdaja")
            self.assertFalse(row["execution_success"])
            record = row["arm_evidence"]["trajectory_artifacts"].pop(
                "azdaja_solo_trace"
            )
            Path(record["path"]).unlink()
            runs.write_bytes(b"".join(SCORE.canonical_json_file_bytes(item) for item in rows))
            runs.chmod(0o600)
            done = claims_root / schedule["schedule_id"] / (row["run_id"] + ".done.json")
            private_json(done, {
                "schedule_id": schedule["schedule_id"],
                "run_id": row["run_id"],
                "row_sha256": SCORE.sha256_bytes(SCORE.canonical_json_bytes(row)),
            })
            with mock.patch.object(SCORE, "load_gold", side_effect=AssertionError("gold read")):
                with self.assertRaisesRegex(
                    SCORE.ScoreError,
                    "valid exact retained AZDAJA_SOLO_TRACE.*including failed rows",
                ):
                    SCORE.build_report(manifest, gold, runs, bootstrap_resamples=1)

    def test_root_token_economy_authority_preference_fallback_and_missing(self):
        jcode = "\n".join((
            json.dumps({"type": "tool_done", "output": "éééé"}),
            json.dumps({"type": "tool_done", "output": "abcd"}),
        )).encode()
        control = SCORE.root_token_economy("jcode-native", {"stdout": jcode})
        self.assertEqual(control["root_tokens"], 2.0)
        self.assertTrue(control["fallback_used"])
        self.assertFalse(control["missing"])
        trace = (json.dumps({"depth": 0, "input_tokens": 123}) + "\n").encode()
        treatment = SCORE.root_token_economy(
            "jcode-azdaja",
            {"azdaja_model_trace": trace, "azdaja_solo_trace": b"not used"},
        )
        self.assertEqual(treatment["root_tokens"], 123)
        self.assertFalse(treatment["fallback_used"])
        prompt = "eight123"
        solo = (
            f"\n=== root request begin request_id=\"x\" model=\"m\" request_chars={len(prompt)} ===\n"
            f"{prompt}\n=== root request end request_id=\"x\" ===\n"
        ).encode()
        fallback = SCORE.root_token_economy(
            "jcode-azdaja", {"azdaja_model_trace": b"", "azdaja_solo_trace": solo}
        )
        self.assertEqual(fallback["root_tokens"], len(prompt) / 4)
        self.assertTrue(fallback["fallback_used"])
        missing = SCORE.root_token_economy(
            "jcode-azdaja", {"azdaja_model_trace": b"", "azdaja_solo_trace": b"bad"}
        )
        self.assertTrue(missing["missing"])
        self.assertIsNotNone(missing["missing_reason"])
        self.assertTrue(missing["authority"])

    def test_operational_failure_normalization_has_precedence_and_retains_raw(self):
        raw = {"kind": "transport", "message": "provider timeout at maximum RLM depth"}
        row = {"execution_success": False, "timed_out": True, "failure": raw}
        audit = {"root_context_leak": {"detected": False}}
        normalized = SCORE.normalize_operational_failure(row, audit)
        self.assertEqual(normalized["category"], "transport")
        self.assertEqual(normalized["raw"], raw)
        raw["message"] = "changed"
        self.assertNotEqual(normalized["raw"], raw)
        leak = SCORE.normalize_operational_failure(
            row, {"root_context_leak": {"detected": True}}
        )
        self.assertEqual(leak["category"], "root_context_leak")

    def test_full_report_has_macro_cells_and_separates_metric_failures(self):
        with tempfile.TemporaryDirectory() as directory:
            artifacts = self.make_artifacts(Path(directory))
            report = SCORE.build_report(
                artifacts[0], artifacts[1], artifacts[2], bootstrap_resamples=20
            )
            self.assertTrue(report["integrity"]["validated"])
            self.assertEqual(report["integrity"]["scheduled_jobs"], 270)
            self.assertTrue(
                report["integrity"]["root_context_leak_scan_complete_before_gold_read"]
            )
            leak_gate = report["integrity"]["root_context_leak_pre_gold_gate"]
            self.assertTrue(leak_gate["complete"])
            self.assertEqual(leak_gate["treatment_terminal_rows"], 90)
            self.assertEqual(leak_gate["valid_exact_retained_solo_trace_rows"], 90)
            self.assertEqual(leak_gate["scanned_rows"], 90)
            self.assertEqual(
                report["integrity"]["scheduled_per_arm"],
                {arm: 90 for arm in SCORE.ARMS},
            )
            self.assertTrue(report["integrity"]["exact_90_per_arm_asserted"])
            self.assertTrue(
                report["integrity"][
                    "route_and_usage_internally_recomputed_from_retained_artifacts"
                ]
            )
            self.assertEqual(
                report["integrity"]["route_and_usage_replay_scope"],
                {
                    "successful_rows_replayed_n": 270,
                    "failed_rows_hash_bound_but_not_route_or_usage_replayed_n": 0,
                },
            )
            stamp = report["candidate_version_stamp"]
            self.assertEqual(set(stamp["components"]), {"azdaja", "config.toml", "SKILL.md"})
            self.assertTrue(stamp["candidate_binary_equals_executed_azdaja"])
            self.assertEqual(
                stamp["candidate_binary"]["sha256"],
                stamp["executed_azdaja"]["sha256"],
            )
            self.assertEqual(len(report["cells"]), 27)
            native = report["arms"]["jcode-native"]["macro_9_cell"]
            self.assertEqual(native["cell_count"], 9)
            self.assertEqual(native["official_ruler_coverage_percent"], 100.0)
            self.assertEqual(native["exact_set_rate"], 1.0)
            native_all = report["arms"]["jcode-native"]["overall_fixed_denominator"]
            self.assertEqual(
                native_all["telemetry_all_attempts"]["usage"]["valid_n"], 90
            )
            self.assertEqual(
                native_all["telemetry_all_attempts"]["usage"]["unconditional_totals"]["total_tokens"],
                9450,
            )
            self.assertEqual(
                native_all["telemetry_all_attempts"]["latency_seconds"]["p95"], 1.5
            )
            treatment = report["arms"]["jcode-azdaja"]["macro_9_cell"]
            self.assertEqual(treatment["official_ruler_coverage_percent"], 100.0)
            self.assertEqual(treatment["exact_set_rate"], 0.0)
            separation = report["arms"]["jcode-azdaja"]["overall_fixed_denominator"]["failure_separation"]
            self.assertEqual(separation["execution_failure_n"], 0)
            self.assertEqual(separation["completed_strict_failure_n"], 90)
            self.assertEqual(separation["completed_official_full_but_strict_failed_n"], 90)
            comparison = report["comparisons"]["jcode-native__minus__jcode-azdaja"]
            self.assertEqual(comparison["paired_fixture_n"], 90)
            self.assertEqual(comparison["metrics"]["exact_set"]["delta"], 1.0)

    def test_execution_failure_is_not_conflated_with_strict_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            artifacts = self.make_artifacts(Path(directory), failed_job=3)
            report = SCORE.build_report(
                artifacts[0], artifacts[1], artifacts[2], bootstrap_resamples=5
            )
            native = report["arms"]["jcode-native"]["overall_fixed_denominator"]
            self.assertEqual(native["execution"]["failed_n"], 1)
            self.assertEqual(native["execution"]["failure_taxonomy"], {"timeout": 1})
            # The terminal output happened to be exact, but end-to-end exactness
            # still fails it while output correctness remains independently visible.
            self.assertEqual(native["output_scores_all_terminal_rows"]["exact_set_n"], 90)
            self.assertEqual(native["end_to_end_fixed_denominator"]["exact_set_n"], 89)
            self.assertEqual(native["failure_separation"]["completed_strict_failure_n"], 0)
            self.assertEqual(native["telemetry_all_attempts"]["usage"]["valid_n"], 89)
            self.assertIsNone(
                native["telemetry_all_attempts"]["usage"]["unconditional_totals"]
            )
            self.assertFalse(
                report["integrity"][
                    "route_and_usage_internally_recomputed_from_retained_artifacts"
                ]
            )
            self.assertEqual(
                report["integrity"]["route_and_usage_replay_scope"],
                {
                    "successful_rows_replayed_n": 269,
                    "failed_rows_hash_bound_but_not_route_or_usage_replayed_n": 1,
                },
            )

    def test_scorer_rejects_candidate_binary_executable_mismatch_before_gold(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest, gold, runs, _, _, _, _ = self.make_artifacts(
                Path(directory), candidate_executable_match=False
            )
            with mock.patch.object(SCORE, "load_gold", side_effect=AssertionError("gold read")):
                with self.assertRaisesRegex(SCORE.ScoreError, "candidate azdaja component"):
                    SCORE.build_report(manifest, gold, runs, bootstrap_resamples=1)

    def test_headline_metrics_keep_90_scheduled_with_88_successes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline = self.make_artifacts(root)
            native_ordinals = [
                row["execution_ordinal"] for row in baseline[6]
                if row["arm"] == "jcode-native"
            ][:2]
        with tempfile.TemporaryDirectory() as directory:
            manifest, gold, runs, _, _, _, _ = self.make_artifacts(
                Path(directory), failed_jobs=set(native_ordinals)
            )
            report = SCORE.build_report(manifest, gold, runs, bootstrap_resamples=1)
            native = report["arms"]["jcode-native"]
            self.assertEqual(native["scheduled_n"], 90)
            self.assertEqual(native["headline"]["executed_n"], 88)
            self.assertEqual(native["execution_rate"], 88 / 90)
            self.assertEqual(native["headline"]["completed_correct_n"], 88)
            self.assertEqual(native["headline"]["completed_accuracy_denominator_n"], 88)
            self.assertEqual(native["completed_accuracy"], 88 / 88)
            self.assertEqual(native["headline"]["end_to_end_correct_n"], 88)
            self.assertEqual(native["headline"]["end_to_end_accuracy_denominator_n"], 90)
            self.assertEqual(native["end_to_end_accuracy"], 88 / 90)

    def test_an_88_row_prefix_is_not_a_fake_complete_suite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, gold, runs, _, _, _, _ = self.make_artifacts(root)
            runs.write_bytes(b"".join(runs.read_bytes().splitlines(keepends=True)[:88]))
            runs.chmod(0o600)
            with mock.patch.object(SCORE, "load_gold", side_effect=AssertionError("gold read")):
                with self.assertRaisesRegex(SCORE.ScoreError, "terminal-complete"):
                    SCORE.build_report(manifest, gold, runs, bootstrap_resamples=1)

    def test_incomplete_runs_are_rejected_before_gold_is_touched(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, gold, runs, _, _, _, _ = self.make_artifacts(root)
            lines = runs.read_bytes().splitlines(keepends=True)
            runs.write_bytes(b"".join(lines[:-1]))
            runs.chmod(0o600)
            with mock.patch.object(SCORE, "load_gold", side_effect=AssertionError("gold read")):
                with self.assertRaisesRegex(SCORE.ScoreError, "terminal-complete"):
                    SCORE.build_report(manifest, gold, runs, bootstrap_resamples=1)

    def test_gold_missing_is_not_observed_until_terminal_validation_finishes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, _, runs, _, _, _, _ = self.make_artifacts(root)
            lines = runs.read_bytes().splitlines(keepends=True)
            runs.write_bytes(b"".join(lines[:-1]))
            runs.chmod(0o600)
            nonexistent = root / "owner-secret-does-not-exist.json"
            with self.assertRaisesRegex(SCORE.ScoreError, "terminal-complete"):
                SCORE.build_report(manifest, nonexistent, runs, bootstrap_resamples=1)



    def test_candidate_config_pins_root_and_repair_models(self):
        mini = (
            b'default_model="gpt-5.6-luna"\n'
            b'jcode_repair_model="gpt-5.4-mini"\n'
        )
        SCORE._validate_candidate_model_config(mini, "gpt-5.4-mini")
        with self.assertRaisesRegex(SCORE.ScoreError, "repair model"):
            SCORE._validate_candidate_model_config(mini, SCORE.MODEL)
        bad_root = (
            b'default_model="gpt-5.4-mini"\n'
            b'jcode_repair_model="gpt-5.4-mini"\n'
        )
        with self.assertRaisesRegex(SCORE.ScoreError, "root model"):
            SCORE._validate_candidate_model_config(bad_root, "gpt-5.4-mini")

    def test_independent_route_allows_mini_only_for_depth_zero_repairs(self):
        def row(depth, category, model, request):
            return {
                "schema_version": 2,
                "event": "model_attempt",
                "timestamp_ms": 1,
                "depth": depth,
                "request_id": request,
                "attempt": 1,
                "category": category,
                "outcome": "succeeded",
                "provider": "OpenAI OAuth",
                "model": model,
            }

        rows = [
            row(0, "turn", SCORE.MODEL, "root"),
            row(0, "repair", "gpt-5.4-mini", "repair"),
            row(1, "turn", SCORE.MODEL, "child"),
        ]
        evidence = {
            "azdaja_model_trace": b"".join(
                SCORE.canonical_json_file_bytes(item) for item in rows
            )
        }
        self.assertTrue(
            SCORE._independent_route("jcode-azdaja", evidence, "gpt-5.4-mini")
        )
        rows[0]["model"] = "gpt-5.4-mini"
        bad_root = {"azdaja_model_trace": b"".join(
            SCORE.canonical_json_file_bytes(item) for item in rows
        )}
        self.assertFalse(
            SCORE._independent_route("jcode-azdaja", bad_root, "gpt-5.4-mini")
        )
        rows[0]["model"] = SCORE.MODEL
        rows[2]["model"] = "gpt-5.4-mini"
        bad_child = {"azdaja_model_trace": b"".join(
            SCORE.canonical_json_file_bytes(item) for item in rows
        )}
        self.assertFalse(
            SCORE._independent_route("jcode-azdaja", bad_child, "gpt-5.4-mini")
        )
        downgraded = row(0, "repair", "gpt-5.4-mini", "downgraded")
        downgraded["schema_version"] = 1
        downgraded_evidence = {
            "azdaja_model_trace": SCORE.canonical_json_file_bytes(downgraded)
        }
        self.assertFalse(
            SCORE._independent_route(
                "jcode-azdaja", downgraded_evidence, "gpt-5.4-mini"
            )
        )

    def test_runner_build_schedule_contract_validates_in_scorer(self):
        runner_spec = importlib.util.spec_from_file_location(
            "azdaja_ruler_run_contract", HERE / "run.py"
        )
        runner = importlib.util.module_from_spec(runner_spec)
        sys.modules[runner_spec.name] = runner
        assert runner_spec.loader is not None
        runner_spec.loader.exec_module(runner)
        with tempfile.TemporaryDirectory() as directory:
            artifacts = self.make_artifacts(Path(directory))
            manifest_path, _, _, _, _, base_schedule, _ = artifacts
            manifest, public = SCORE.load_public_manifest(manifest_path)
            runner_fixtures = tuple(
                runner.PublicFixture(
                    fixture_id=fixture_id,
                    task=item["task"],
                    target_length=item["target_length"],
                    payload_path=item["_payload_path"],
                    payload_data=item["_payload_bytes"],
                    payload_sha256=item["payload_sha256"],
                    payload_bytes=item["payload_bytes"],
                    construction_tokens=item["construction_tokens"],
                    row_length=item["row_length"],
                )
                for fixture_id, item in public.items()
            )
            suite = runner.PublicSuite(
                path=manifest_path,
                sha256=SCORE.sha256_bytes(SCORE.canonical_json_file_bytes(manifest)),
                manifest=manifest,
                fixtures=runner_fixtures,
            )
            random_names = [f"{index:032x}.txt" for index in range(90)]
            schedule = runner.build_schedule(
                suite,
                seed=base_schedule["configuration"]["seed"],
                timeout=1800,
                candidate=base_schedule["configuration"]["candidate"],
                candidate_source_path=base_schedule["configuration"]["candidate_source_path"],
                controller=base_schedule["configuration"]["controller"],
                controller_source_paths=base_schedule["configuration"]["controller_source_paths"],
                executables=base_schedule["configuration"]["executables"],
                random_names=random_names,
            )
            jobs, arms = SCORE.validate_schedule(
                schedule, manifest_path, manifest, public
            )
            self.assertEqual(len(jobs), 270)
            self.assertEqual(arms, SCORE.ARMS)



    def test_raw_row_semantics_are_recomputed(self):
        with tempfile.TemporaryDirectory() as directory:
            artifacts = self.make_artifacts(Path(directory))
            gold = json.loads(artifacts[1].read_text(encoding="utf-8"))
            receipts = {
                (receipt["task"], receipt["target_length"]): receipt
                for receipt in gold["provenance"]["pool_receipts"]
            }
            for item in gold["fixtures"]:
                if item["task"] != "niah_multikey_3":
                    continue
                raw = SCORE._decode_json(item["raw_row_utf8"], "test raw row")
                raw["index"] += 1
                pool_row = receipts[(item["task"], item["target_length"])]["rows"][item["ordinal"]]
                with self.assertRaises(SCORE.ScoreError):
                    SCORE._validate_raw_task_semantics(
                        item["task"], item["target_length"], item["ordinal"], raw, pool_row
                    )
                break

    def test_run_process_state_and_artifact_hashes_fail_closed(self):
        mutations = ("seed", "timed_out_type", "exit_code_type", "process_state", "artifact")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                artifacts = self.make_artifacts(Path(directory))
                manifest_path, _, _, _, _, schedule, rows = artifacts
                _, fixtures = SCORE.load_public_manifest(manifest_path)
                candidate = json.loads(json.dumps(rows))
                if mutation == "seed":
                    candidate[0]["schedule_seed"] += 1
                elif mutation == "timed_out_type":
                    candidate[0]["timed_out"] = 0
                elif mutation == "exit_code_type":
                    candidate[0]["exit_code"] = True
                elif mutation == "process_state":
                    candidate[0]["exit_code"] = 1
                else:
                    candidate[0]["arm_evidence"]["trajectory_artifacts"]["stdout"]["sha256"] = "f" * 64
                with self.assertRaises(SCORE.ScoreError):
                    SCORE.validate_run_rows(candidate, schedule["jobs"], schedule, fixtures)

    def test_json_decoder_rejects_nested_lone_surrogates(self):
        with self.assertRaises(SCORE.ScoreError):
            SCORE._decode_json('{"outer":["\\ud800"]}', "surrogate test")

    def test_claim_receipts_are_exact_and_terminal(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, gold, runs, _, claims_root, schedule, _ = self.make_artifacts(root)
            claims = claims_root / schedule["schedule_id"]
            first = schedule["jobs"][0]
            (claims / (first["run_id"] + ".done.json")).unlink()
            with mock.patch.object(SCORE, "load_gold", side_effect=AssertionError("gold read")):
                with self.assertRaisesRegex(SCORE.ScoreError, "exact terminal 2N set"):
                    SCORE.build_report(manifest, gold, runs, bootstrap_resamples=1)

    def test_hash_identity_tampering_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, gold, runs, schedule_path, _, schedule, _ = self.make_artifacts(root)
            schedule["configuration"]["model"] = "tampered"
            private_json(schedule_path, schedule)
            with self.assertRaisesRegex(SCORE.ScoreError, "schedule SHA-256"):
                SCORE.build_report(manifest, gold, runs, bootstrap_resamples=1)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, gold, runs, _, _, _, _ = self.make_artifacts(root)
            document = json.loads(gold.read_text(encoding="utf-8"))
            document["fixtures"][0]["outputs"][0] = "ffffffff-ffff-4fff-8fff-ffffffffffff"
            private_json(gold, document)
            with self.assertRaisesRegex(SCORE.ScoreError, "exact gold file SHA-256"):
                SCORE.build_report(manifest, gold, runs, bootstrap_resamples=1)

    def test_manifest_identity_and_payload_hash_are_reverified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, gold, runs, _, _, _, _ = self.make_artifacts(root)
            document = json.loads(manifest.read_text(encoding="utf-8"))
            payload = manifest.parent / document["fixtures"][0]["payload"]
            private_text(payload, payload.read_text(encoding="utf-8") + "tamper")
            with self.assertRaisesRegex(SCORE.ScoreError, "payload bytes mismatch"):
                SCORE.build_report(manifest, gold, runs, bootstrap_resamples=1)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, gold, runs, _, _, _, _ = self.make_artifacts(root)
            document = json.loads(gold.read_text(encoding="utf-8"))
            document["manifest_identity_sha256"] = "f" * 64
            private_json(gold, document)
            public = json.loads(manifest.read_text(encoding="utf-8"))
            public["gold_sha256"] = SCORE.sha256_path(gold)
            private_json(manifest, public)
            # The schedule still binds the old exact public manifest, so the
            # public mutation is caught before gold. This proves the pre-gold
            # binding is authoritative rather than trusting the supplied pair.
            with self.assertRaisesRegex(SCORE.ScoreError, "public manifest SHA-256"):
                SCORE.build_report(manifest, gold, runs, bootstrap_resamples=1)


    def test_pinned_provenance_and_hmac_selection_tampering_is_rejected(self):
        mutations = ("source", "master", "seed", "selection", "fixture_id")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                manifest_path, gold_path, _, _, _, _, _ = self.make_artifacts(root)
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                _, fixtures = SCORE.load_public_manifest(manifest_path)
                gold = json.loads(gold_path.read_text(encoding="utf-8"))
                if mutation == "source":
                    gold["provenance"]["upstream"]["files"]["LICENSE"] = "f" * 64
                elif mutation == "master":
                    gold["provenance"]["generation_plan"]["master_key_hex"] = "f" * 64
                elif mutation == "seed":
                    gold["provenance"]["generation_plan"]["cells"][0]["generator_seed"] += 1
                elif mutation == "selection":
                    gold["fixtures"][0]["selection"]["hmac_rank_sha256"] = "f" * 64
                else:
                    gold["fixtures"][0]["id"] = "rxm-" + "f" * 32
                private_json(gold_path, gold)
                manifest["gold_sha256"] = SCORE.sha256_path(gold_path)
                with self.assertRaises(SCORE.ScoreError):
                    SCORE.load_gold(gold_path, manifest, fixtures)

    def test_success_telemetry_is_required_and_usage_is_arm_normalized(self):
        mutations = ("route", "usage_missing", "usage_total", "empty_response")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                manifest, gold, runs, _, claims_root, schedule, rows = self.make_artifacts(root)
                target = next(row for row in rows if row["execution_success"])
                if mutation == "route":
                    target["route_assertion"]["asserted"] = False
                elif mutation == "usage_missing":
                    target["usage"] = None
                elif mutation == "usage_total":
                    target["usage"]["total_tokens"] += 1
                else:
                    target["response"] = ""
                runs.write_bytes(b"".join(SCORE.canonical_json_file_bytes(row) for row in rows))
                runs.chmod(0o600)
                # Refresh completion receipts so validation reaches telemetry.
                claims = claims_root / schedule["schedule_id"]
                for row, job in zip(rows, schedule["jobs"]):
                    private_json(
                        claims / (job["run_id"] + ".done.json"),
                        {
                            "schedule_id": schedule["schedule_id"],
                            "run_id": job["run_id"],
                            "row_sha256": SCORE.sha256_bytes(SCORE.canonical_json_bytes(row)),
                        },
                    )
                with self.assertRaises(SCORE.ScoreError):
                    SCORE.build_report(manifest, gold, runs, bootstrap_resamples=1)

    def test_candidate_snapshot_is_exact_and_source_extras_cannot_change_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest, _, _, _, _, schedule, _ = self.make_artifacts(Path(directory))
            document, fixtures = SCORE.load_public_manifest(manifest)
            SCORE.validate_schedule(schedule, manifest, document, fixtures)
            source = Path(schedule["configuration"]["candidate_source_path"])
            private_text(source / "another-unselected-file", "ignored")
            SCORE.validate_schedule(schedule, manifest, document, fixtures)
            snapshot = Path(schedule["configuration"]["candidate"]["snapshot_root"])
            private_text(snapshot / "undeclared", "extra")
            with self.assertRaises(SCORE.ScoreError):
                SCORE.validate_schedule(schedule, manifest, document, fixtures)
            (snapshot / "undeclared").unlink()
            component = snapshot / "SKILL.md"
            component.chmod(0o600)
            component.write_bytes(component.read_bytes() + b"tamper")
            component.chmod(0o400)
            with self.assertRaises(SCORE.ScoreError):
                SCORE.validate_schedule(schedule, manifest, document, fixtures)

    def test_prime_bundle_recursive_inventory_and_rehash_are_authoritative(self):
        with tempfile.TemporaryDirectory() as directory:
            _, _, _, _, _, schedule, _ = self.make_artifacts(Path(directory))
            identity = schedule["configuration"]["executables"]["prime-agent"]
            executable = Path(identity["path"])
            bundle = identity["bundle"]
            SCORE._validate_prime_bundle(bundle, executable)
            extra = Path(bundle["root"]) / "extra"
            private_text(extra, "undeclared")
            extra.chmod(0o400)
            with self.assertRaises(SCORE.ScoreError):
                SCORE._validate_prime_bundle(bundle, executable)
            extra.unlink()
            executable.chmod(0o700)
            executable.write_bytes(executable.read_bytes() + b"tamper")
            executable.chmod(0o500)
            with self.assertRaises(SCORE.ScoreError):
                SCORE._validate_prime_bundle(bundle, executable)

    def test_authority_ndjson_rejects_every_malformed_nonempty_line(self):
        for arm in SCORE.ARMS:
            with self.subTest(arm=arm), tempfile.TemporaryDirectory() as directory:
                manifest, _, _, _, _, schedule, rows = self.make_artifacts(Path(directory))
                _, fixtures = SCORE.load_public_manifest(manifest)
                row = next(item for item in rows if item["arm"] == arm)
                artifact_name = (
                    "azdaja_model_trace" if arm == "jcode-azdaja" else "stdout"
                )
                record = row["arm_evidence"]["trajectory_artifacts"][artifact_name]
                path = Path(record["path"])
                path.write_bytes(b"not-json\n" + path.read_bytes())
                path.chmod(0o600)
                record["bytes"] = path.stat().st_size
                record["sha256"] = SCORE.sha256_path(path)
                with self.assertRaisesRegex(SCORE.ScoreError, "parse"):
                    SCORE.validate_run_rows(rows, schedule["jobs"], schedule, fixtures)

    def test_artifact_paths_inodes_and_run_inventories_are_exact(self):
        mutations = ("extra_file", "alias", "unexpected_key", "extra_run_directory")
        for mutation in mutations:
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                manifest, _, _, _, _, schedule, rows = self.make_artifacts(Path(directory))
                _, fixtures = SCORE.load_public_manifest(manifest)
                row = rows[0]
                trajectories = row["arm_evidence"]["trajectory_artifacts"]
                run_directory = Path(trajectories["stdout"]["path"]).parent
                if mutation == "extra_file":
                    private_text(run_directory / "undeclared.log", "extra")
                elif mutation == "alias":
                    trajectories["stderr"] = copy.deepcopy(trajectories["stdout"])
                elif mutation == "unexpected_key":
                    trajectories["unexpected"] = copy.deepcopy(trajectories["stdout"])
                else:
                    (run_directory.parent / "undeclared-run").mkdir(mode=0o700)
                with self.assertRaises(SCORE.ScoreError):
                    SCORE.validate_run_rows(rows, schedule["jobs"], schedule, fixtures)

    def test_redistribution_commitments_files_and_public_inventory_are_exact(self):
        for mutation in ("commitment", "file", "inventory", "payload_inventory"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                manifest, *_ = self.make_artifacts(Path(directory))
                if mutation == "commitment":
                    document = json.loads(manifest.read_text(encoding="utf-8"))
                    document["redistribution_files"]["THIRD_PARTY_NOTICES.md"] = "f" * 64
                    private_json(manifest, document)
                elif mutation == "file":
                    private_text(manifest.parent / "THIRD_PARTY_NOTICES.md", "tampered")
                elif mutation == "inventory":
                    private_text(manifest.parent / "undeclared.txt", "extra")
                else:
                    private_text(manifest.parent / "payloads" / "undeclared.txt", "extra")
                with self.assertRaises(SCORE.ScoreError):
                    SCORE.load_public_manifest(manifest)

    def test_synthetic_terminal_success_and_failure_integrate_all_arms(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = self.make_artifacts(Path(directory))
            first_ordinal = {
                arm: next(row["execution_ordinal"] for row in baseline[6] if row["arm"] == arm)
                for arm in SCORE.ARMS
            }
        for arm, ordinal in first_ordinal.items():
            with self.subTest(arm=arm), tempfile.TemporaryDirectory() as directory:
                manifest, gold, runs, _, _, _, _ = self.make_artifacts(
                    Path(directory), failed_job=ordinal
                )
                report = SCORE.build_report(
                    manifest, gold, runs, bootstrap_resamples=1
                )
                execution = report["arms"][arm]["overall_fixed_denominator"]["execution"]
                self.assertEqual(execution["failed_n"], 1)
                self.assertEqual(execution["completed_n"], 89)

    @unittest.skipUnless(os.name == "posix", "POSIX permissions")
    def test_owner_only_gold_is_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, gold, runs, _, _, _, _ = self.make_artifacts(root)
            gold.chmod(0o644)
            with self.assertRaisesRegex(SCORE.ScoreError, "owner-only gold"):
                SCORE.build_report(manifest, gold, runs, bootstrap_resamples=1)

    def test_cli_exclusively_creates_private_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest, gold, runs, _, _, _, _ = self.make_artifacts(root)
            output = root.resolve() / "scores.json"
            result = SCORE.main(
                [
                    "--manifest", str(manifest),
                    "--gold", str(gold),
                    "--runs", str(runs),
                    "--output", str(output),
                    "--bootstrap-resamples", "3",
                ]
            )
            self.assertEqual(result, 0)
            self.assertTrue(output.is_file())
            if os.name == "posix":
                self.assertEqual(stat.S_IMODE(output.stat().st_mode), 0o600)
            self.assertEqual(SCORE.main(
                [
                    "--manifest", str(manifest),
                    "--gold", str(gold),
                    "--runs", str(runs),
                    "--output", str(output),
                    "--bootstrap-resamples", "1",
                ]
            ), 2)


if __name__ == "__main__":
    unittest.main()
