"""Exercise the production Android master-list HTTPS bridge without network or game assets.

The test compiles host_https.c, replacing only the TLS transport with a fake.
It checks the master signature headers and JSON body survive the host/guest
boundary, capacity is forwarded, and a failed request clears output state.
"""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

HARNESS = r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "port/linux/src/update.h"

static int fail, empty, calls;
static unsigned long requested_limit;

int update_https_request(const char *method, const char *url, const char *headers,
    const void *body, unsigned long body_size, unsigned long maximum,
    struct update_response *response, char *error, int error_size)
{
    const char *json = "{\"servers\":[]}";
    assert(strcmp(method, "GET") == 0);
    assert(strcmp(url, "https://master.example/servers") == 0);
    assert(headers == NULL && body == NULL && body_size == 0);
    calls++;
    requested_limit = maximum;
    if (fail) {
        snprintf(error, (size_t)error_size, "TLS verification failed");
        return 0;
    }
    memset(response, 0, sizeof(*response));
    response->status = empty ? 204 : 200;
    snprintf(response->headers, sizeof(response->headers),
        "Signature: ed25519:abc123\nSignature-Key: master-key\n");
    response->body_size = empty ? 0 : strlen(json);
    response->body = malloc(response->body_size + 1);
    assert(response->body);
    memcpy(response->body, json, response->body_size);
    response->body[response->body_size] = 0;
    return 1;
}

#include "port/android/host/host_https.c"

int main(void)
{
    char headers[4096], body[128], error[256];
    int status = -1, length = -1;
    memset(body, 0x7f, sizeof(body));
    assert(host_https_get("https://master.example/servers", &status, headers,
        sizeof(headers), body, sizeof(body), &length, error, sizeof(error)));
    assert(calls == 1 && requested_limit == sizeof(body));
    assert(status == 200 && length == (int)strlen("{\"servers\":[]}"));
    assert(memcmp(body, "{\"servers\":[]}", (size_t)length) == 0);
    assert((unsigned char)body[length] == 0x7f);
    assert(strstr(headers, "Signature: ed25519:abc123\n") != NULL);
    assert(strstr(headers, "Signature-Key: master-key\n") != NULL);

    fail = 1;
    status = -1;
    length = -1;
    assert(!host_https_get("https://master.example/servers", &status, headers,
        sizeof(headers), body, sizeof(body), &length, error, sizeof(error)));
    assert(status == 0 && length == 0);
    assert(strcmp(error, "TLS verification failed") == 0);

    fail = 0;
    empty = 1;
    status = -1;
    length = -1;
    assert(host_https_get("https://master.example/servers", &status, headers,
        sizeof(headers), body, sizeof(body), &length, error, sizeof(error)));
    assert(status == 204 && length == 0);
    return 0;
}
'''


def main():
    with tempfile.TemporaryDirectory() as directory:
        source = Path(directory) / "master_bridge_test.c"
        program = Path(directory) / "master_bridge_test"
        source.write_text(HARNESS)
        subprocess.run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror",
                        "-I", str(ROOT), "-I", str(ROOT / "port/android/include"),
                        str(source), "-o", str(program)], check=True)
        subprocess.run([str(program)], check=True)
    print("Android master HTTPS bridge: headers, body, bounds and errors passed.")


if __name__ == "__main__":
    main()
