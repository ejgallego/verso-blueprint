from __future__ import annotations

from playwright.sync_api import Page


def record_runtime_errors(page: Page) -> list[str]:
    errors: list[str] = []

    page.on("pageerror", lambda exc: errors.append(str(exc)))

    def on_console(msg) -> None:
        if msg.type == "error":
            errors.append(msg.text)

    page.on("console", on_console)
    return errors


def assert_no_runtime_errors(errors: list[str]) -> None:
    relevant = [
        err
        for err in errors
        if "cancelChildHide" in err or "ReferenceError" in err or "Uncaught" in err
    ]
    assert not relevant, "\n".join(relevant)
