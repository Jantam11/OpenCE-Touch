#!/usr/bin/env python3
"""Exercise the production map picker's navigation/selection without game assets."""
import shutil
import subprocess
import tempfile
from pathlib import Path
from test_virtual_keyboard_input import function, c_block
ROOT=Path(__file__).resolve().parent.parent
PRELUDE=r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef int boolean;
#define TRUE 1
#define FALSE 0
#define NONE (-1)
#define CUSTOM_EDITION_MAPS_MAXIMUM 16
#define NUMBER_OF_GAME_DIFFICULTY_LEVELS 4
#define NUMBER_OF_SINGLE_PLAYER_LEVELS 2
#define NUMBEROF(a) (sizeof(a)/sizeof((a)[0]))
#define MIN(a,b) ((a)<(b)?(a):(b))
#define PIN(v,a,b) ((v)<(a)?(a):((v)>(b)?(b):(v)))
struct overlay_repeat {boolean held;unsigned long next_time;};
struct widget_instance {struct {struct {short selected_index;} list;} parameters;};
static unsigned long now=1000;
static int chosen,cooperative,opened,went_back,posted,valid=1,available=1,enabled=1;
static short difficulty_seen;
unsigned long system_milliseconds(void) {return now;}
boolean custom_edition_maps_stock(short n) {return n==2;}
short custom_edition_maps_level_display_index(short n) {return n;}
short custom_edition_maps_display_index(const char *s) {return s[0]=='a'?10:11;}
const char *main_get_solo_level_name(short n) {return n?"b":"a";}
long custom_edition_maps_count(boolean campaign) {(void)campaign;return 1;}
short custom_edition_maps_display_index_of(boolean campaign,short n) {(void)campaign;return 12+n;}
const char *custom_edition_maps_level_name(short n) {(void)n;return "campaign";}
boolean ui_widget_port_multiplayer_level_choose(const char *n) {(void)n;chosen++;return valid;}
boolean ui_widget_port_cooperative_level_choose(const char *n,short d) {(void)n;cooperative++;difficulty_seen=d;return valid;}
boolean ui_widget_port_open_from_top(const char *n) {(void)n;opened++;return TRUE;}
void ui_widget_port_go_back_from_top(void) {went_back++;}
void event_manager_post_button(short c,short b) {(void)c;(void)b;posted++;}
void event_manager_flush(void) {}
boolean ui_overlay_available(void) {return available;}
int config_boolean(const char *name) {(void)name;return enabled;}
static char *names[]={"xbox0","xbox1","pcstock","cecustom"};
char **ui_widget_port_multiplayer_levels(short *n,short *x) {*n=4;*x=2;return names;}
void *global_network_game_server_get(void) {return (void *)1;}
boolean network_game_is_splitscreen_local(void) {return FALSE;}
short main_get_difficulty(void) {return 1;}
void map_screen_note_online_games(void) {}
void map_screen_go_back(void) {ui_widget_port_go_back_from_top();}
'''
TESTS=r'''
int main(void) {
 struct map_entry entries[MAXIMUM_LEVELS];struct widget_instance xbox={0};
 available=0;assert(!map_screen_open());available=1;enabled=0;assert(!map_screen_open());enabled=1;
 assert(map_screen_open());assert(map_screen.active&&map_screen.step==STEP_KINDS);
 pick();assert(map_screen.step==STEP_KINDS); /* opening press cannot also select */
 now+=OPEN_SETTLE;pick();assert(map_screen.step==STEP_COOPERATIVE_MODES);
 pick();pick();assert(map_screen.step==STEP_CAMPAIGN_LEVELS&&map_screen.count==2);
 valid=0;pick();assert(map_screen.active&&!opened&&cooperative==1);valid=1;pick();assert(!map_screen.active&&opened==1&&difficulty_seen==1&&cooperative==2);
 assert(map_screen_open());now+=OPEN_SETTLE;map_screen.kind_selected=1;pick();assert(map_screen.step==STEP_CATEGORIES);
 assert(category_levels(0,entries)==3&&category_levels(1,entries)==1);
 map_screen.category_selected=1;pick();assert(map_screen.count==1&&map_screen.entries[0].level==3);
 pick();assert(!map_screen.active&&chosen==1&&opened==2);
 assert(map_screen_open());now+=OPEN_SETTLE;map_screen.step=STEP_MAPS;map_screen.count=0;pick();assert(map_screen.active&&chosen==1);
 map_screen.xbox_list=&xbox;map_screen.count=1;map_screen.entries[0].level=2;
 pick();assert(!map_screen.active&&xbox.parameters.list.selected_index==2&&posted==1);
 assert(map_screen_open());map_screen.step=STEP_CAMPAIGN_LEVELS;back();assert(map_screen.step==STEP_CAMPAIGN_CATEGORIES);
 back();back();assert(map_screen.step==STEP_KINDS);back();assert(!map_screen.active&&went_back==1);
 assert(map_screen_open());map_screen.hosting=0;map_screen.step=STEP_CATEGORIES;back();assert(!map_screen.active&&went_back==2);
 assert(map_screen_open());map_screen.xbox_list=&xbox;
 map_screen_list_disposed(NULL);assert(map_screen.active&&map_screen.xbox_list==&xbox);
 map_screen_list_disposed(&xbox);assert(!map_screen.active&&!map_screen.xbox_list);
 assert(map_screen_open());map_screen_close();assert(!map_screen.active);
 puts("PASS: disabled fallback, settled opening, stock/CE filtering, co-op/PvP selection, empty lists, back navigation and cleanup");
 return 0;
}
'''
def main():
    text=(ROOT/'port/linux/game/map_screen.c').read_text()
    constants=text[text.index('enum\n{'):text.index("/* in the game's level order")]
    entry_start=text.index('struct map_entry\n');entry_brace=text.index('{',entry_start)
    entry=text[entry_start:entry_brace]+c_block(text,entry_brace)+';'
    globals_start=text.index('static struct\n');globals_end=text.index('/* ---------- private code */',globals_start)
    definitions='\n'.join(function(text,n) for n in ('level_vanilla','category_levels','campaign_levels','list_open','leave','pick','back','map_screen_close','map_screen_list_disposed','map_screen_open'))
    with tempfile.TemporaryDirectory(prefix='opence-map-picker-') as d:
        unit=Path(d)/'maps.c';exe=Path(d)/'maps'
        unit.write_text(PRELUDE+constants+entry+text[globals_start:globals_end]+definitions+TESTS)
        cc=shutil.which('clang') or shutil.which('gcc')
        subprocess.run([cc,'-std=gnu11','-Wall','-Werror',str(unit),'-o',str(exe)],check=True)
        subprocess.run([str(exe)],check=True)
if __name__=='__main__':main()
