//! Optional, bounded static lint for the native text-hash contract.
//!
//! This is not a Python typechecker or a sandbox. It never rewrites or executes a
//! program. Any syntactic binding of `sha256`, even in an unrelated nested scope,
//! makes the lint abstain for the whole program. Known misuse in dead code is
//! still linted. Aliased calls and unknown argument types are intentionally not
//! inferred. Monty remains authoritative for Python compilation and execution.

use anyhow::{Result, bail};
use ruff_python_ast::{
    self as ast, Expr, ExprContext, Stmt,
    visitor::{self, Visitor},
};

#[derive(Default)]
struct HashContract {
    hash_shadowed: bool,
    ctx_shadowed: bool,
    bad_result_method: bool,
    bytes_argument: bool,
    encoded_ctx: bool,
    depth: usize,
    too_deep: bool,
}

impl HashContract {
    fn bind(&mut self, name: &str) {
        self.hash_shadowed |= name == "sha256";
        self.ctx_shadowed |= name == "ctx";
    }

    fn enter(&mut self) -> bool {
        if self.depth >= 256 {
            self.too_deep = true;
            return false;
        }
        self.depth += 1;
        true
    }
}

fn native_hash_call(expr: &Expr) -> Option<&ast::ExprCall> {
    if let Expr::Call(call) = expr
        && matches!(call.func.as_ref(), Expr::Name(name) if name.id == "sha256")
    {
        Some(call)
    } else {
        None
    }
}

impl<'a> Visitor<'a> for HashContract {
    fn visit_stmt(&mut self, stmt: &'a Stmt) {
        if !self.enter() {
            return;
        }
        match stmt {
            Stmt::FunctionDef(def) => self.bind(def.name.as_str()),
            Stmt::ClassDef(def) => self.bind(def.name.as_str()),
            Stmt::Global(def) => {
                for name in &def.names {
                    self.bind(name.as_str());
                }
            }
            Stmt::Nonlocal(def) => {
                for name in &def.names {
                    self.bind(name.as_str());
                }
            }
            _ => {}
        }
        visitor::walk_stmt(self, stmt);
        self.depth -= 1;
    }

    fn visit_expr(&mut self, expr: &'a Expr) {
        if !self.enter() {
            return;
        }
        if let Expr::Name(name) = expr {
            if name.ctx != ExprContext::Load {
                self.bind(name.id.as_str());
            }
            // Future or foreign dynamic namespace mutation is not statically resolved.
            if matches!(name.id.as_str(), "globals" | "locals" | "exec" | "eval") {
                self.hash_shadowed = true;
                self.ctx_shadowed = true;
            }
        }
        if let Expr::Attribute(attr) = expr
            && matches!(attr.attr.as_str(), "hexdigest" | "digest")
            && native_hash_call(&attr.value).is_some()
        {
            self.bad_result_method = true;
        }
        if let Some(call) = native_hash_call(expr)
            && let Some(argument) = call.arguments.args.first()
        {
            self.bytes_argument |= matches!(argument, Expr::BytesLiteral(_));
            if let Expr::Call(encoded) = argument
                && let Expr::Attribute(method) = encoded.func.as_ref()
                && method.attr.as_str() == "encode"
            {
                self.bytes_argument |= matches!(method.value.as_ref(), Expr::StringLiteral(_));
                self.encoded_ctx |=
                    matches!(method.value.as_ref(), Expr::Name(name) if name.id == "ctx");
            }
        }
        visitor::walk_expr(self, expr);
        self.depth -= 1;
    }

    fn visit_parameter(&mut self, parameter: &'a ast::Parameter) {
        self.bind(parameter.name.as_str());
        visitor::walk_parameter(self, parameter);
    }

    fn visit_alias(&mut self, alias: &'a ast::Alias) {
        if alias.name.as_str() == "*" {
            self.hash_shadowed = true;
            self.ctx_shadowed = true;
        }
        let name = alias.asname.as_ref().unwrap_or(&alias.name);
        self.bind(name.as_str().split('.').next().unwrap_or_default());
    }

    fn visit_except_handler(&mut self, handler: &'a ast::ExceptHandler) {
        let ast::ExceptHandler::ExceptHandler(handler) = handler;
        if let Some(name) = &handler.name {
            self.bind(name.as_str());
        }
        if let Some(expr) = &handler.type_ {
            self.visit_expr(expr);
        }
        self.visit_body(&handler.body);
    }

    fn visit_pattern(&mut self, pattern: &'a ast::Pattern) {
        if !self.enter() {
            return;
        }
        match pattern {
            ast::Pattern::MatchAs(p) => {
                if let Some(name) = &p.name {
                    self.bind(name.as_str());
                }
            }
            ast::Pattern::MatchStar(p) => {
                if let Some(name) = &p.name {
                    self.bind(name.as_str());
                }
            }
            ast::Pattern::MatchMapping(p) => {
                if let Some(name) = &p.rest {
                    self.bind(name.as_str());
                }
            }
            _ => {}
        }
        visitor::walk_pattern(self, pattern);
        self.depth -= 1;
    }

    fn visit_type_param(&mut self, parameter: &'a ast::TypeParam) {
        match parameter {
            ast::TypeParam::TypeVar(p) => self.bind(p.name.as_str()),
            ast::TypeParam::ParamSpec(p) => self.bind(p.name.as_str()),
            ast::TypeParam::TypeVarTuple(p) => self.bind(p.name.as_str()),
        }
        visitor::walk_type_param(self, parameter);
    }
}

pub(super) fn validate_native_hash(code: &str) -> Result<()> {
    let parsed = ruff_python_parser::parse_module(code).map_err(|_| {
        anyhow::anyhow!("optional solo native-call preflight could not parse program")
    })?;
    let mut scan = HashContract::default();
    scan.visit_body(&parsed.syntax().body);
    if scan.too_deep {
        bail!("optional solo native-call preflight exceeds nesting limit")
    }
    if !scan.hash_shadowed
        && (scan.bad_result_method
            || scan.bytes_argument
            || (scan.encoded_ctx && !scan.ctx_shadowed))
    {
        bail!(
            "optional solo native hash contract: {}",
            super::NATIVE_HASH_CONTRACT
        )
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn known_native_hash_misuses_are_rejected() {
        for code in [
            "FINAL(sha256(ctx.encode('utf-8')).hexdigest())",
            "FINAL(sha256(ctx).hexdigest())",
            "FINAL(sha256(ctx).digest())",
            "FINAL((sha256 (ctx))\n .hexdigest())",
            "FINAL(sha256(ctx.encode()))",
            "FINAL(sha256('literal'.encode()))",
            "FINAL(sha256(b'literal'))",
            "FINAL(f'{sha256(ctx).hexdigest()}')",
            "if False:\n    FINAL(sha256(ctx).hexdigest())",
            "def unused():\n    return sha256(ctx).hexdigest()",
        ] {
            let error = validate_native_hash(code).unwrap_err().to_string();
            assert!(error.contains("native hash contract"), "{code}: {error}");
        }
    }

    #[test]
    fn valid_calls_literals_comments_and_unknown_types_are_not_rewritten() {
        for code in [
            "FINAL(sha256(ctx))",
            "FINAL(sha256('Unicode 🦀'))",
            "note = 'sha256(ctx.encode()).hexdigest()'\nFINAL(sha256(ctx))",
            "note = '''sha256(ctx).hexdigest()\nsha256(ctx.encode())'''\nFINAL(note)",
            "# sha256(ctx).hexdigest()\nFINAL(sha256(ctx))",
            "FINAL(f'{{sha256(ctx).hexdigest()}}')",
            "FINAL(other.sha256(ctx).hexdigest())",
            "FINAL(sha256(other.encode()))",
            "h = sha256\nFINAL(h(ctx).hexdigest())", // Aliases are not inferred.
            "FINAL(sha256(other))",                  // Unknown argument types stay runtime-owned.
        ] {
            validate_native_hash(code).unwrap_or_else(|e| panic!("{code}: {e}"));
        }
    }

    #[test]
    fn every_syntactic_binding_abstains_conservatively_across_scopes() {
        for binder in [
            "sha256 = other",
            "sha256: object",
            "sha256 += other",
            "del sha256",
            "a, sha256 = pair",
            "(sha256 := other)",
            "for sha256 in values:\n    pass",
            "async def f():\n    async for sha256 in values:\n        pass",
            "with manager as sha256:\n    pass",
            "async def f():\n    async with manager as sha256:\n        pass",
            "try:\n    pass\nexcept Exception as sha256:\n    pass",
            "try:\n    pass\nexcept* Exception as sha256:\n    pass",
            "import sha256.submodule",
            "import module as sha256",
            "from module import sha256",
            "from module import other as sha256",
            "from module import *",
            "def sha256(value):\n    return value",
            "class sha256:\n    pass",
            "def f(sha256):\n    pass",
            "def f(sha256, /):\n    pass",
            "def f(*, sha256):\n    pass",
            "def f(*sha256):\n    pass",
            "def f(**sha256):\n    pass",
            "f = lambda sha256: sha256",
            "result = [sha256 for sha256 in values]",
            "result = {sha256: 1 for sha256 in values}",
            "match value:\n    case sha256:\n        pass",
            "match value:\n    case [*sha256]:\n        pass",
            "match value:\n    case {'key': _, **sha256}:\n        pass",
            "def f[sha256]():\n    pass",
            "def f[*sha256]():\n    pass",
            "def f[**sha256]():\n    pass",
            "type sha256 = int",
            "global sha256",
            "def f():\n    nonlocal sha256",
            "namespace = globals()",
            "namespace = locals()",
            "execute = exec",
            "evaluate = eval",
        ] {
            let code = format!("{binder}\nFINAL(sha256(ctx).hexdigest())");
            validate_native_hash(&code).unwrap_or_else(|e| panic!("{binder}: {e}"));
        }
    }

    #[test]
    fn rebound_ctx_is_unknown_but_native_hash_result_stays_a_string() {
        validate_native_hash("ctx = other\nFINAL(sha256(ctx.encode()))").unwrap();
        assert!(validate_native_hash("ctx = other\nFINAL(sha256(ctx).hexdigest())").is_err());
        validate_native_hash("def f(ctx):\n    return ctx\nFINAL(sha256(ctx.encode()))").unwrap();
    }

    #[test]
    fn parser_and_visitor_fail_closed_without_evaluation() {
        assert!(validate_native_hash("FINAL(").is_err());
        let parser_limited = format!("FINAL({}0)", "+".repeat(300));
        assert!(validate_native_hash(&parser_limited).is_err());
        let code = format!("FINAL({})", vec!["0"; 300].join("+"));
        assert!(
            validate_native_hash(&code)
                .unwrap_err()
                .to_string()
                .contains("nesting limit")
        );
    }

    #[test]
    fn default_configuration_does_not_apply_optional_lint() {
        let code = "FINAL(sha256(ctx.encode()).hexdigest())";
        let mut cfg = super::super::Config::default();
        super::super::validate_solo_python_for_config(code, &cfg).unwrap();
        cfg.judge.enabled = Some(true);
        assert!(super::super::validate_solo_python_for_config(code, &cfg).is_err());
    }
}
