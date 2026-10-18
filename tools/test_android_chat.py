"""Editable-overlay chat pointer: consume typing taps, normalize and clear them."""
from pathlib import Path
import subprocess
import tempfile
from harness import function
source = (Path(__file__).resolve().parents[1] / 'port/linux/src/sdl_platform.c').read_text()
code = r"""
#include <assert.h>
#include <math.h>
#define SDL_BUTTON_LEFT 1
static int input_lock, chat_pointer_taps;
static float chat_pointer_x, chat_pointer_y;
static void pthread_mutex_lock(int *p) {(void)p;}
static void pthread_mutex_unlock(int *p) {(void)p;}
""" + function(source, 'chat_pointer_event') + function(source, 'platform_chat_taps') + r"""
int main(void) {
 float x,y;
 assert(!chat_pointer_event(0,0,1,600,200,1200,400));
 assert(!platform_chat_taps(&x,&y));
 assert(chat_pointer_event(1,1,1,600,200,1200,400));
 assert(!platform_chat_taps(&x,&y));
 assert(chat_pointer_event(1,0,1,600,200,1200,400));
 assert(platform_chat_taps(&x,&y)==1 && x==.5f && y==.5f);
 assert(!platform_chat_taps(&x,&y));
 assert(chat_pointer_event(1,0,2,600,200,1200,400));
 assert(!platform_chat_taps(&x,&y));
 chat_pointer_event(1,0,1,NAN,200,1200,400);
 chat_pointer_event(1,0,1,600,200,0,400);
 assert(!platform_chat_taps(&x,&y));
 chat_pointer_event(1,0,1,600,200,1200,400);
 assert(!chat_pointer_event(0,0,1,0,0,1200,400));
 assert(!platform_chat_taps(&x,&y));
 return 0;
}
"""
with tempfile.TemporaryDirectory() as d:
 p=Path(d);(p/'chat.c').write_text(code)
 subprocess.run(['cc','-std=c99','-Wall','-Wextra','-Werror',str(p/'chat.c'),'-o',str(p/'chat')],check=True)
 subprocess.run([str(p/'chat')],check=True)
print('Editable-overlay chat taps, consumption, normalization and stale-input checks passed.')
