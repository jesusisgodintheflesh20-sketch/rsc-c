#include "../vendor/src/entity.h"
#include "../vendor/src/protocol/opcodes.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
int main(void) {
    struct player p = {0};
    p.protocol_rev = 203;
    init_opcodes_203();
    assert(player_send_sound(&p, "fish") == 0);
    const unsigned char expected[] = {5, 'h', 204, 'f', 'i', 's'};
    assert(p.outbuf_len == sizeof(expected));
    assert(memcmp(p.outbuf, expected, sizeof(expected)) == 0);
    puts("PASS: offline sound event maps to the client sound packet");
}
