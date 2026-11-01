#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "lighting-bake.h"
static int16_t ground[LIGHTING_GRID][LIGHTING_GRID];
static uint16_t walls[LIGHTING_GRID][LIGHTING_GRID];
int main(void) {
    assert(lighting_bake_vertex(ground, walls, 48, 48) == 0);
    walls[49][48] = 200;
    int near_wall = lighting_bake_vertex(ground, walls, 48, 48);
    assert(near_wall > 0 && near_wall <= 18);
    walls[49][48] = 0;
    ground[49][48] = 200;
    assert(lighting_bake_vertex(ground, walls, 48, 48) > 0);
    ground[49][48] = 0;
    walls[60][48] = 500;
    assert(lighting_bake_vertex(ground, walls, 48, 48) == 0);
    assert(lighting_bake_vertex(ground, walls, 0, 0) == 0);
    puts("PASS: region occlusion rays respond to nearby walls and terrain");
}
