#include "../../src/game-data.h"
#include <assert.h>
#include <ctype.h>
static const char *directory;
void strtolower(char *s) { for (; *s; ++s) *s = tolower((unsigned char)*s); }
int get_unsigned_byte(void *data, size_t offset, size_t size) {
    assert(offset < size); return ((unsigned char *)data)[offset];
}
int get_unsigned_short(void *data, size_t offset, size_t size) {
    return (get_unsigned_byte(data,offset,size)<<8)|get_unsigned_byte(data,offset+1,size);
}
int get_unsigned_int(void *data, size_t offset, size_t size) {
    return ((unsigned)get_unsigned_short(data,offset,size)<<16)|get_unsigned_short(data,offset+2,size);
}
void *load_data(const char *name, size_t extra, void *archive, size_t *size) {
    (void)archive;
    char path[4096]; snprintf(path,sizeof(path),"%s/%s",directory,name);
    FILE *f=fopen(path,"rb"); assert(f);
    fseek(f,0,SEEK_END); long len=ftell(f); rewind(f);
    void *data=calloc(1,len+extra); assert(data);
    assert(fread(data,1,len,f)==(size_t)len); fclose(f);
    if(size)*size=len;
    return data;
}
int main(int argc, char **argv) {
    assert(argc==2); directory=argv[1];
    game_data_load_data(NULL,0,46);
    assert(game_data.item_count==545 && game_data.npc_count==250);
    assert(game_data.animation_count==149 && game_data.object_count==261);
    assert(game_data.prayer_count==14 && game_data.spell_count==28);
    assert(!strcmp(game_data.items[0].name,"Iron Mace"));
    assert(game_data.items[0].sprite==0 && game_data.items[0].base_price==63);
    assert(game_data.npcs[0].width==168 && game_data.npcs[0].height==192);
    assert(game_data.npcs[0].attack==21 && game_data.npcs[0].defense==23);
    assert(!strcmp(game_data.spells[0].name,"Wind strike"));
    assert(game_data.spells[0].runes_required==2);
    assert(game_data.roofs[0].height==10 && game_data.roofs[0].fill==6);
    puts("PASS: actual client loads converted 2001 definitions without bounds errors");
}
