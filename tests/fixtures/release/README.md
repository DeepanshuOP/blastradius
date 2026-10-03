# `release/` fixtures

`pseudonym_vectors.csv` holds the frozen expected output of
`analysis/build_release.py::pseudonymise` under the test key

    br-bench-test-key-do-not-use

Each `pseudonym` was produced independently of the Python implementation, with

    printf '%s' '<login>' | openssl dgst -sha256 -hmac 'br-bench-test-key-do-not-use' -r | cut -c1-16

so the test compares our code against a reference HMAC, not against itself.

The logins are deliberately not drawn from the corpus. `author_login` is the one
column the release exists to pseudonymise, so checking real logins into `tests/`
would reintroduce exactly the disclosure the pseudonymisation removes. What the
fixture has to exercise is the login *shapes* the corpus actually contains — a
plain login, a bot login with brackets, a single character, and non-ASCII — and
those are reproduced here without naming anyone.

If a value in this file ever has to change, the pseudonym mapping has changed,
every previously published bundle disagrees with the new one, and that is a
release-breaking decision, not a test fix.
