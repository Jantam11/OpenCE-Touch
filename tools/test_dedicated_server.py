#!/usr/bin/env python3
"""Run the playlist director's production C with deterministic clocks and a fake network.
No game assets are needed. Network transport and live play remain integration checks.
"""
from test_virtual_keyboard_input import function
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRELUDE = r'''
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <wchar.h>
#include <stdarg.h>
typedef int boolean;
typedef unsigned short word;
typedef unsigned char byte;
#define TRUE 1
#define FALSE 0
#define PIN(v,a,b) ((v)<(a)?(a):((v)>(b)?(b):(v)))
#define NUMBEROF(a) (sizeof(a)/sizeof((a)[0]))
#define csmemset memset
#define csmemcmp memcmp
#define ustrncpy wcsncpy
#define _stricmp strcasecmp
#define _error_silent 0
struct game_variant {struct {int teams;} universal_variant; int valid;};
struct network_game {int player_count;byte maximum_players,minimum_players;wchar_t name[16];};
struct network_game_server {struct network_game game;word state;};
static struct network_game_server server;
static struct network_game_server *current;
static unsigned long clock_ms=100;
static int menu_active=1,paused,ready=1,starts,ends,resets,public_listing;
static long score;
static char selected_map[128];
void error(int kind,const char *format,...) {(void)kind;(void)format;}
unsigned long system_milliseconds(void) {return clock_ms;}
void Sleep(unsigned long n) {clock_ms+=n;}
struct network_game_server *global_network_game_server_get(void) {return current;}
void *global_network_game_client_get(void) {return current;}
word network_game_server_get_state(struct network_game_server *s,short *out) {(void)out;return s->state;}
struct network_game *network_game_server_get_game(struct network_game_server *s) {return &s->game;}
void network_game_server_change_map_name(struct network_game_server *s,const char *map) {(void)s;snprintf(selected_map,sizeof(selected_map),"%s",map);}
void network_game_server_change_game_variant(struct network_game_server *s,struct game_variant *v) {(void)s;(void)v;}
void network_game_server_pause_countdown(struct network_game_server *s,boolean pause) {(void)s;paused=pause;}
void network_game_server_dedicated_start_countdown(struct network_game_server *s) {(void)s;if(!paused&&ready)starts++;}
void p2p_set_hosting_allowed(int value) {(void)value;}
void p2p_set_hosting_public(int value) {public_listing=value;}
void player_ui_fast_setup_network_server(void) {current=&server;}
void player_ui_set_game_variant(struct game_variant *v) {(void)v;}
void main_set_multiplayer_map_name(const char *map) {(void)map;}
void game_engine_override_map_name(const char *map) {(void)map;}
long game_engine_total_score(void) {return score;}
boolean main_menu_is_active(void) {return menu_active;}
boolean bink_playback_active(void) {return FALSE;}
boolean custom_edition_maps_level_campaign(const char *map) {return strstr(map,"campaign")!=NULL;}
boolean cache_files_map_plays_multiplayer(const char *map,char *build) {(void)build;return strstr(map,"missing")==NULL;}
void game_engine_get_variant_by_name(struct game_variant *v,const char *name) {
 memset(v,0,sizeof(*v));if(!strcmp(name,"slayer")){v->valid=1;}else if(!strcmp(name,"ctf")){v->valid=1;v->universal_variant.teams=1;}
}
boolean game_engine_running(void) {return TRUE;}
boolean game_engine_can_score(void) {return TRUE;}
void game_engine_end_game(void) {ends++;}
boolean network_game_server_reset_to_pregame(struct network_game_server *s) {s->state=0;resets++;return TRUE;}
static FILE *playlist_open(const char *path,const char *mode) {(void)path;return fopen("playlist.txt",mode);}
#define fopen playlist_open
'''
TESTS = r'''
#undef fopen
static void reset(void) {
 memset(&dedicated,0,sizeof(dedicated));memset(&server,0,sizeof(server));
 current=NULL;clock_ms=100;starts=ends=resets=paused=0;score=0;menu_active=ready=1;
}
int main(void) {
 FILE *p=fopen("playlist.txt","w");assert(p);
 fputs("# rotation\nbloodgulch slayer\nsidewinder ctf\ntimberland@ce slayer # CE\n",p);fclose(p);
 unsetenv("HALO_DEDICATED");reset();assert(!dedicated_server_active());dedicated_server_update();assert(!current);
 setenv("HALO_DEDICATED","playlists/test.txt",1);
 setenv("HALO_DEDICATED_MINIMUM_PLAYERS","2",1);setenv("HALO_DEDICATED_MAXIMUM_PLAYERS","1",1);
 setenv("HALO_DEDICATED_PUBLIC","off",1);setenv("HALO_DEDICATED_IDLE_LIMIT","1",1);
 reset();assert(dedicated_server_active());assert(dedicated.entry_count==3);
 assert(!strcmp(dedicated.maps[0],"levels\\test\\bloodgulch\\bloodgulch"));
 assert(!strcmp(dedicated.maps[2],"timberland@ce"));assert(dedicated.maximum_players==2);
 menu_active=0;dedicated_server_update();assert(!current);
 menu_active=1;dedicated_server_update();assert(current==&server&&!public_listing);
 server.game.player_count=1;dedicated_server_update();assert(paused&&!starts);
 server.game.player_count=2;ready=0;dedicated_server_update();assert(!paused&&!starts);
 ready=1;dedicated_server_update();assert(starts&&server.game.maximum_players==2);
 assert(strstr(selected_map,"bloodgulch"));
 server.state=1;dedicated_server_update();clock_ms+=50000;score=1;dedicated_server_update();assert(!ends);
 clock_ms+=60001;dedicated_server_update();assert(ends==1);
 server.state=2;dedicated_server_update();clock_ms+=20001;dedicated_server_update();assert(resets==1);
 dedicated_server_update();assert(dedicated.entry==1&&strstr(selected_map,"sidewinder"));
 server.game.player_count=1;dedicated_server_update();assert(dedicated.entry==2&&!dedicated.entry_teams);
 server.state=1;server.game.player_count=0;dedicated_server_update();clock_ms+=30001;dedicated_server_update();assert(ends==2);
 /* Bad entries retry at a bounded rate; no countdown starts on an invalid map. */
 reset();assert(dedicated_server_active());current=&server;server.game.player_count=2;
 strcpy(dedicated.maps[0],"missing");dedicated_server_update();assert(!starts&&dedicated.entry==1);
 clock_ms+=1000;dedicated_server_update();assert(!starts&&dedicated.entry==1);
 clock_ms+=5000;dedicated_server_update();assert(starts);
 reset();assert(dedicated_server_active());strcpy(dedicated.variants[0],"invalid");assert(!set_entry(&server));
 strcpy(dedicated.maps[1],"campaign");assert(!set_entry(&server));
 setenv("HALO_DEDICATED_IDLE_LIMIT","999999",1);reset();assert(dedicated_server_active());assert(dedicated.idle_limit==1440);
 p=fopen("playlist.txt","w");fputs("# empty\n",p);fclose(p);reset();assert(!dedicated_server_active());
 puts("PASS: opt-in hosting, playlists, limits, readiness, rotation, idle/empty recovery and invalid-map retry");
 return 0;
}
'''

def main():
    text=(ROOT/'server/src/dedicated.c').read_text()
    source=text[text.index('enum\n{'):text.index('\n#else\nint dedicated_server_active')]
    with tempfile.TemporaryDirectory(prefix='opence-server-') as directory:
        unit=Path(directory)/'server.c'; executable=Path(directory)/'server'
        unit.write_text(PRELUDE+source+TESTS)
        cc=shutil.which('clang') or shutil.which('gcc')
        if not cc: raise SystemExit('clang or gcc is required')
        subprocess.run([cc,'-std=gnu11','-Wall','-Werror',str(unit),'-o',str(executable)],check=True)
        subprocess.run([str(executable)],cwd=directory,check=True)
        # Only the local dedicated host may lack a player. Remote empty
        # machines must still block countdown, as must an ordinary empty host.
        ownership = (ROOT/'source/networking/network_server_manager.c').read_text()
        unit.write_text(r'''
#include <assert.h>
typedef int boolean;
#define TRUE 1
#define FALSE 0
#define MAXIMUM_NETWORK_MACHINE_COUNT 3
#define MAXIMUM_NETWORK_PLAYER_COUNT 3
struct network_player {int valid,machine_index;};
struct network_game_server_client_machine {int joined,local,machine_index;};
struct network_game_server {struct {struct network_player players[3];} game;struct network_game_server_client_machine client_machines[3];};
static int dedicated;
boolean dedicated_server_active(void) {return dedicated;}
boolean network_player_is_valid(struct network_player *p) {return p->valid;}
boolean network_game_server_client_machine_is_joined_to_game(struct network_game_server *s,struct network_game_server_client_machine *m) {(void)s;return m->joined;}
boolean network_game_server_client_machine_is_local(struct network_game_server *s,struct network_game_server_client_machine *m) {(void)s;return m->local;}
''' + function(ownership,'server_has_a_player_on_each_machine') + r'''
int main(void) {
 struct network_game_server s={0};
 s.client_machines[0].joined=1;s.client_machines[0].local=1;
 assert(!server_has_a_player_on_each_machine(&s));
 dedicated=1;assert(server_has_a_player_on_each_machine(&s));
 s.client_machines[1].joined=1;s.client_machines[1].machine_index=1;
 assert(!server_has_a_player_on_each_machine(&s));
 s.game.players[0].valid=1;s.game.players[0].machine_index=1;
 assert(server_has_a_player_on_each_machine(&s));
 dedicated=0;assert(!server_has_a_player_on_each_machine(&s));
 s.game.players[1].valid=1;s.game.players[1].machine_index=0;
 assert(server_has_a_player_on_each_machine(&s));
 return 0;
}
''')
        subprocess.run([cc,'-std=gnu11','-Wall','-Werror',str(unit),'-o',str(executable)],check=True)
        subprocess.run([str(executable)],check=True)
        print('PASS: dedicated empty-host exception preserves remote and ordinary-host player readiness')


if __name__=='__main__':main()
