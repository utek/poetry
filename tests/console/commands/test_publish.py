import pytest

from poetry.utils._compat import PY36
from poetry.utils._compat import Path


@pytest.mark.skipif(
    not PY36, reason="Improved error rendering is only available on Python >=3.6"
)
def test_publish_returns_non_zero_code_for_upload_errors(app, app_tester, http):
    http.register_uri(
        http.POST, "https://upload.pypi.org/legacy/", status=400, body="Bad Request"
    )

    exit_code = app_tester.execute("publish --username foo --password bar")

    assert 1 == exit_code

    expected = """
Publishing simple-project (1.2.3) to PyPI


  UploadError

  HTTP Error 400: Bad Request
"""

    assert expected in app_tester.io.fetch_output()


@pytest.mark.skipif(
    PY36, reason="Improved error rendering is not available on Python <3.6"
)
def test_publish_returns_non_zero_code_for_upload_errors_older_python(
    app, app_tester, http
):
    http.register_uri(
        http.POST, "https://upload.pypi.org/legacy/", status=400, body="Bad Request"
    )

    exit_code = app_tester.execute("publish --username foo --password bar")

    assert 1 == exit_code

    expected = """
Publishing simple-project (1.2.3) to PyPI


UploadError

HTTP Error 400: Bad Request
"""

    assert app_tester.io.fetch_output() == expected


def test_publish_with_cert(app_tester, mocker):
    publisher_publish = mocker.patch("poetry.publishing.Publisher.publish")

    app_tester.execute("publish --cert path/to/ca.pem")

    assert [
        (None, None, None, Path("path/to/ca.pem"), None, False)
    ] == publisher_publish.call_args


def test_publish_with_client_cert(app_tester, mocker):
    publisher_publish = mocker.patch("poetry.publishing.Publisher.publish")

    app_tester.execute("publish --client-cert path/to/client.pem")
    assert [
        (None, None, None, None, Path("path/to/client.pem"), False)
    ] == publisher_publish.call_args


def test_publish_dry_run(app_tester, http):
    http.register_uri(
        http.POST, "https://upload.pypi.org/legacy/", status=403, body="Forbidden"
    )

    exit_code = app_tester.execute("publish --dry-run --username foo --password bar")

    assert 0 == exit_code

    output = app_tester.io.fetch_output()
    error = app_tester.io.fetch_error()

    assert "Publishing simple-project (1.2.3) to PyPI" in output
    assert "- Uploading simple-project-1.2.3.tar.gz" in error
    assert "- Uploading simple_project-1.2.3-py2.py3-none-any.whl" in error


def test_publish_with_publish_default_set(app, app_tester, http):
    app.poetry.package.publish_default = "private_pypi"
    app_tester.execute("publish")

    expected = """
Publishing simple-project (1.2.3) to private_pypi

[RuntimeError]
Repository private_pypi is not defined
"""

    assert app_tester.io.fetch_output() == expected
