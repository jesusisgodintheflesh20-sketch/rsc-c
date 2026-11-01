#ifndef RSC_LIGHTING_BAKE_H
#define RSC_LIGHTING_BAKE_H
#include <stdint.h>
#define LIGHTING_GRID 96
/* Trace short upward rays through a coarse static heightfield. Heights and wall
 * occluders are world units. The returned value is a shade in the range 0..18. */
static int lighting_bake_vertex(const int16_t ground[LIGHTING_GRID][LIGHTING_GRID],
                                const uint16_t walls[LIGHTING_GRID][LIGHTING_GRID],
                                int x, int z) {
    static const int direction[8][2] = {
        {1,0}, {1,1}, {0,1}, {-1,1}, {-1,0}, {-1,-1}, {0,-1}, {1,-1}
    };
    int blocked = 0;
    int origin = ground[x][z];
    for (int d = 0; d < 8; d++) {
        for (int slope = 0; slope < 2; slope++) {
            for (int step = 1; step <= 3; step++) {
                int sx = x + direction[d][0] * step;
                int sz = z + direction[d][1] * step;
                if (sx < 0 || sz < 0 || sx >= LIGHTING_GRID || sz >= LIGHTING_GRID)
                    break;
                int ray_height = origin + 18 + step * (slope ? 80 : 35);
                if (ground[sx][sz] > ray_height ||
                    (walls[sx][sz] && ground[sx][sz] + walls[sx][sz] > ray_height)) {
                    blocked++;
                    break;
                }
            }
        }
    }
    return (blocked * 18 + 8) / 16;
}
#endif
