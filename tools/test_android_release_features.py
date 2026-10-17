"""Production display options: defaults, bounds and no delay on a network game."""
from pathlib import Path
import subprocess
import tempfile
from harness import function

ROOT = Path(__file__).resolve().parents[1]

def main():
    source = (ROOT / 'source/main/main.c').read_text()
    game = (ROOT / 'source/game/game.c').read_text()
    timers = (ROOT / 'port/linux/game/powerup_timers.c').read_text()
    code = r'''
#include <assert.h>
#include <math.h>
#include <string.h>
#include <strings.h>
typedef float real;
#define PIN(v,l,h) ((v)<(l)?(l):((v)>(h)?(h):(v)))
#define valid_real(v) isfinite(v)
#define _stricmp strcasecmp
#define _game_connection_local 0
#define TICKS_PER_SECOND 30
static double value;
static unsigned long changes;
static int connection, split;
static double config_real(const char *name) {(void)name;return value;}
static unsigned long config_changes(void) {return changes;}
static const char *tag_name_strip_path(const char *path) {const char *p=strrchr(path,'\\');return p?p+1:path;}
static int game_connection(void) {return connection;}
static int network_game_is_splitscreen_local(void) {return split;}
''' + function(source,'far_clip_distance_floor') + '\n' + function(game,'game_loading_screen_hold_milliseconds') + '\n' + function(timers,'powerup_timers_seconds') + r'''
int main(void) {
 value=1024;changes++;assert(far_clip_distance_floor()==1024);
 value=4096;changes++;assert(far_clip_distance_floor()==4096);
 value=1;changes++;assert(far_clip_distance_floor()==1024);
 value=20000;changes++;assert(far_clip_distance_floor()==10000);
 value=NAN;changes++;assert(far_clip_distance_floor()==1024);
 value=3;assert(game_loading_screen_hold_milliseconds("levels\\a10\\a10")==3000);
 connection=1;assert(!game_loading_screen_hold_milliseconds("levels\\a10\\a10"));
 split=1;assert(game_loading_screen_hold_milliseconds("levels\\a10\\a10")==3000);
 assert(!game_loading_screen_hold_milliseconds("levels\\ui\\ui"));
 value=0;assert(!game_loading_screen_hold_milliseconds("levels\\a10\\a10"));
 value=-1;assert(!game_loading_screen_hold_milliseconds("a10"));
 value=NAN;assert(!game_loading_screen_hold_milliseconds("a10"));
 value=40;assert(game_loading_screen_hold_milliseconds("a10")==30000);
 assert(powerup_timers_seconds(0)==0&&powerup_timers_seconds(1)==1);
 assert(powerup_timers_seconds(30)==1&&powerup_timers_seconds(31)==2);
 return 0;
}
'''
    with tempfile.TemporaryDirectory() as folder:
        p=Path(folder);(p/'test.c').write_text(code)
        subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror',str(p/'test.c'),'-lm','-o',str(p/'test')],check=True)
        subprocess.run([str(p/'test')],check=True)
    print('Draw-distance bounds, timer rounding and local-only optional loading delay passed.')

if __name__ == '__main__':
    main()
