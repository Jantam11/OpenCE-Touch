"""Run mobile feature regressions against production Java and host C, without game assets."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "port/android/app/src/main/java/com/halo/decomp"

JAVA_TEST = r'''
package com.halo.decomp;
import java.nio.*;
import java.nio.file.*;
import java.nio.channels.*;
import java.nio.charset.*;
import java.util.*;
public class MobileCheck {
 static void require(boolean b) { if (!b) throw new AssertionError(); }
 static void rejects(String s) { try { TouchConfiguration.decode(s); throw new AssertionError("accepted invalid layout"); } catch (IllegalArgumentException expected) {} }
 static void entry(ByteBuffer b, int at, String name, int sector, int size, boolean dir, int right) {
  byte[] text=name.getBytes(StandardCharsets.US_ASCII);
  b.putShort(at+2,(short)right);b.putInt(at+4,sector);b.putInt(at+8,size);
  b.put(at+12,(byte)(dir?16:0));b.put(at+13,(byte)text.length);
  for(int i=0;i<text.length;i++)b.put(at+14+i,text[i]);
 }
 public static void main(String[] args) throws Exception {
  TouchConfiguration c=new TouchConfiguration();
  TouchConfiguration.Button button=new TouchConfiguration.Button();
  button.id="fire";button.label="FIRE";button.action=1016;button.x=.9f;button.y=.7f;button.radius=.065f;button.opacity=.6f;
  c.buttons.add(button);c.gyro=true;c.fov=85;c.icons=false;
  String saved=c.encode(); TouchConfiguration d=TouchConfiguration.decode(saved);
  require(d.buttons.size()==1&&d.buttons.get(0).action==1016&&d.buttons.get(0).opacity==.6f&&d.gyro&&d.fov==85&&!d.icons);
  rejects(saved.replace("control.0.x=0.9","control.0.x=NaN"));
  rejects(saved.replace("control.0.action=1016","control.0.action=65"));
  rejects(saved.replace("count=1","count=66"));
  rejects(saved.replace("version=1","version=9"));
  rejects(saved.replace("gyroscope=true","gyroscope=maybe"));
  rejects("x".repeat(65537));
  TouchConfiguration imported=TouchConfiguration.decode("format=halo-touch-layout\nversion=4\ncount=3\ncontrol.0.type=16\ncontrol.0.x=480\ncontrol.0.y=270\ncontrol.1.type=17\ncontrol.1.x=960\ncontrol.1.y=540\ncontrol.2.type=18\n");
  require(imported.buttons.get(0).kind==1&&imported.buttons.get(0).x==.5f&&imported.buttons.get(1).action==1016&&imported.buttons.get(2).action==2000);
  require(imported.buttons.size()==4&&imported.buttons.get(3).kind==2);
  require(TouchConfiguration.decode(imported.encode()).buttons.get(3).kind==2);
  rejects("format=halo-touch-layout\nversion=4\ncount=2\ncontrol.0.type=16\ncontrol.1.type=16\n");
  rejects("format=halo-touch-layout\nversion=4\ncount=1\ncontrol.0.type=0\ncontrol.0.visible=false\n");
  GyroscopeAim gyro=new GyroscopeAim(); float[] delta=new float[2];
  require(!gyro.sample(1_000_000_000L,1,2,0,delta));
  require(gyro.sample(1_050_000_000L,1,2,0,delta));require(Math.abs(delta[0]+.1f)<.0001&&Math.abs(delta[1]+.05f)<.0001);
  require(!gyro.sample(2_000_000_000L,1,2,0,delta)); // resume gap
  require(!gyro.sample(2_050_000_000L,1,2,1,delta)); // rotation change
  require(gyro.sample(2_100_000_000L,1,2,1,delta));require(delta[0]>0&&delta[1]<0);
  require(!gyro.sample(2_150_000_000L,Float.NaN,2,1,delta));
  gyro.reset(); require(!gyro.sample(3_000_000_000L,.001f,.002f,0,delta));
  require(!gyro.sample(3_050_000_000L,.001f,.002f,0,delta));
  Path root=Paths.get(args[0]), init=root.resolve("init.txt");String own="; My settings\nset player_magnetism 1\n";
  Files.writeString(init,own);StartupCheats cheats=new StartupCheats(init);cheats.toggle(0);cheats.toggle(14);
  require(Files.readString(init).startsWith(own));require(new StartupCheats(init).enabled(0)&&new StartupCheats(init).enabled(14));
  cheats.toggle(0);require(!new StartupCheats(init).enabled(0));
  Files.writeString(init,own+StartupCheats.BEGIN);try {new StartupCheats(init).toggle(1);throw new AssertionError();}catch(java.io.IOException expected){}
  require(Files.readString(init).equals(own+StartupCheats.BEGIN));
  // A synthetic XDVDFS image proves the movie-only importer leaves maps/profiles alone.
  ByteBuffer image=ByteBuffer.allocate(44*2048).order(ByteOrder.LITTLE_ENDIAN);
  byte[] magic="MICROSOFT*XBOX*MEDIA".getBytes(StandardCharsets.US_ASCII);
  for(int i=0;i<magic.length;i++){image.put(0x10000+i,magic[i]);image.put(0x107ec+i,magic[i]);}
  image.putInt(0x10014,34);image.putInt(0x10018,64);
  entry(image,34*2048,"maps",35,32,true,8);entry(image,34*2048+32,"bink",36,32,true,0);
  entry(image,35*2048,"ui.map",40,4,false,0);entry(image,36*2048,"intro.bik",41,5,false,0);
  image.putInt(40*2048,12345);for(int i=0;i<5;i++)image.put(41*2048+i,(byte)(i+1));
  Path iso=root.resolve("test.xiso"), data=root.resolve("data");Files.write(iso,image.array());
  Files.createDirectories(data.resolve("maps"));Files.writeString(data.resolve("maps/ui.map"),"keep existing maps");
  Files.writeString(data.resolve("profile.bin"),"keep profile");
  try(FileChannel channel=FileChannel.open(iso)){XisoExtractor.extractMovies(channel,data.toFile(),(name,done,total)->require(done<=total&&total==5));}
  require(Files.readString(data.resolve("maps/ui.map")).equals("keep existing maps"));
  require(Files.readString(data.resolve("profile.bin")).equals("keep profile"));
  require(Arrays.equals(Files.readAllBytes(data.resolve("bink/intro.bik")),new byte[]{1,2,3,4,5}));
  Path fresh=root.resolve("fresh");try(FileChannel channel=FileChannel.open(iso)){XisoExtractor.extractMaps(channel,fresh.toFile(),(name,done,total)->require(done<=total&&total==9));}
  require(Files.size(fresh.resolve("maps/ui.map"))==4&&Files.size(fresh.resolve("bink/intro.bik"))==5);
  System.out.println("Portable layout, gyroscope, startup cheats and disc import checks passed.");
 }
}
'''

C_TEST = r'''
#include <assert.h>
#include "port/android/host/host_movie.c"
#include "port/android/host/host_mobile.c"
void host_logf(int level, const char *fmt, ...) {(void)level;(void)fmt;}
int main(void) {
 const char *asset;
 strcpy(movie_assets[0].name,"INTRO.BIK");strcpy(movie_assets[1].name,"intro_fr.bik");movie_asset_count=2;
 assert(movie_resolve("d:\\bink\\intro.bik",&asset)==1&&!strcmp(asset,"INTRO.BIK"));
 assert(movie_resolve("d:\\bink\\introfr.bik",&asset)==1&&!strcmp(asset,"intro_fr.bik"));
 assert(!host_movie_exists("intro_es.bik")&&!host_movie_exists("intro_bad.bik"));
 int movie=host_movie_open("intro.bik");assert(movie==1);
 assert(Java_com_halo_decomp_MoviePlayer_nativePoll(NULL,NULL)==1);
 Java_com_halo_decomp_MoviePlayer_nativeProgress(NULL,NULL,movie,100,200);
 assert(host_movie_frame(movie)==host_movie_frames(movie)/2);
 Java_com_halo_decomp_MoviePlayer_nativeFinished(NULL,NULL,movie);
 assert(host_movie_finished(movie)&&host_movie_frame(movie)==host_movie_frames(movie)-1);
 assert(!Java_com_halo_decomp_MoviePlayer_nativePoll(NULL,NULL));
 movie=host_movie_open("intro.bik");assert(movies[movie].duration_ms==0);
 movie_opened_ms=movie_now_ms()-6000;host_movie_frame(movie);assert(host_movie_finished(movie));
 movie=host_movie_open("intro.bik");host_movie_close(movie);assert(!Java_com_halo_decomp_MoviePlayer_nativePoll(NULL,NULL));
 Java_com_halo_decomp_TouchControls_nativeFieldOfView(NULL,NULL,90);assert(host_touch_field_of_view()==90);
 Java_com_halo_decomp_TouchControls_nativeFieldOfView(NULL,NULL,0);assert(host_touch_field_of_view()==90);
 host_touch_ui_context(0,0);Java_com_halo_decomp_TouchControls_nativeCameraMode(NULL,NULL);assert(host_touch_camera_read()==1);assert(!host_touch_camera_read());
 Java_com_halo_decomp_TouchControls_nativeCameraMode(NULL,NULL);host_touch_ui_context(1,1);assert(!host_touch_camera_read());
 assert(!Java_com_halo_decomp_TouchControls_nativeCheatRequest(NULL,NULL,-1,1));
 assert(Java_com_halo_decomp_TouchControls_nativeCheatRequest(NULL,NULL,2,1));
 assert(!Java_com_halo_decomp_TouchControls_nativeCheatRequest(NULL,NULL,2,0));
 int commands[16];assert(host_touch_cheats_read(commands)==4&&commands[2]==1);assert(!host_touch_cheats_read(commands));
 host_touch_cheat_result(2,1);assert(Java_com_halo_decomp_TouchControls_nativeCheatStatus(NULL,NULL,2)==1);
 host_touch_rumble(65535,0);assert(Java_com_halo_decomp_TouchControls_nativeRumble(NULL,NULL)==255);
 host_touch_rumble(0,0);assert(!Java_com_halo_decomp_TouchControls_nativeRumble(NULL,NULL));
 return 0;
}
'''

def test_singleplayer_cheats(folder):
    source = (ROOT / "source/game/cheats.c").read_text()
    start = source.index("void android_touch_cheats_update(void)")
    end = source.index("\n#endif", start)
    program = r'''#include <assert.h>
#include <string.h>
typedef int boolean;
#define FALSE 0
#define TRUE 1
#define NONE -1
#define _game_connection_local 0
static struct {boolean deathless_player,jetpack,infinite_ammo,bump_possession,super_jump,reflexive_damage_effects,medusa,omnipotent,controller_enabled,bottomless_clip;} cheat;
static unsigned int android_startup_pending,android_cheat_owned;
static int android_startup_flags[10];
static boolean android_startup_loaded,android_cheat_previous[10];
static struct {long unit_index;} player={0};
static struct {struct {long cluster_index;} location;} camera={{0}};
static int connection,client,result,one_shots;
static unsigned int requests;
static int requested[16],synced[16];
static unsigned int host_touch_cheats_read(int commands[16]){memcpy(commands,requested,sizeof(requested));unsigned int bits=requests;requests=0;return bits;}
static long local_player_get_player_index(int i){(void)i;return 0;}
static void *player_get(long i){(void)i;return &player;}
static int game_connection(void){return connection;}
static void cheats_network_client_enforce(void){if(client)memset(&cheat,0,sizeof(cheat));}
static void host_touch_cheat_result(int i,int value){(void)i;result=value;}
static void host_touch_cheat_sync(int i,int value){synced[i]=value;}
static void cheat_active_camouflage_local_player(int i){(void)i;one_shots++;}
static void cheat_active_camouflage(void){one_shots++;}
static void cheat_all_powerups(void){one_shots++;}
static void cheat_all_vehicles(void){one_shots++;}
static void cheat_all_weapons(void){one_shots++;}
static void cheat_teleport_to_camera(void){one_shots++;}
static void *observer_get_camera(int i){(void)i;return &camera;}
'''
    # Production getters return typed pointers; mirror those types in the harness.
    program = program.replace('static struct {long unit_index;} player', 'struct test_player {long unit_index;};static struct test_player player')
    program = program.replace('static struct {struct {long cluster_index;} location;} camera', 'struct test_camera {struct {long cluster_index;} location;};static struct test_camera camera')
    program = program.replace('static void *player_get', 'static struct test_player *player_get').replace('static void *observer_get_camera', 'static struct test_camera *observer_get_camera')
    program += source[start:end] + r'''
int main(void){
 // UI flags are reversible when leaving campaign, including when hosting.
 cheat.jetpack=1;requests=5;requested[0]=requested[2]=1;android_touch_cheats_update();
 assert(cheat.deathless_player&&cheat.infinite_ammo&&cheat.jetpack&&android_cheat_owned==5);
 connection=1;requests=1;android_touch_cheats_update();
 assert(!cheat.deathless_player&&!cheat.infinite_ammo&&cheat.jetpack&&!android_cheat_owned&&result==-1);
 requests=1u<<14;android_touch_cheats_update();assert(one_shots==0&&result==-1);
 // Startup choices wait for a playable local unit and preserve prior values.
 connection=0;player.unit_index=NONE;android_startup_loaded=1;android_startup_flags[0]=1;android_startup_pending=1u<<14;
 android_touch_cheats_update();assert(android_startup_loaded&&!cheat.deathless_player&&one_shots==0);
 player.unit_index=0;android_touch_cheats_update();assert(!android_startup_loaded&&cheat.deathless_player&&!cheat.jetpack&&one_shots==1);
 android_touch_cheats_update();assert(one_shots==1);
 connection=1;android_touch_cheats_update();assert(!cheat.deathless_player&&cheat.jetpack);
 // A joined client still obeys the upstream enforcement after restoration.
 connection=0;requests=2;requested[1]=0;android_touch_cheats_update();
 connection=1;client=1;android_touch_cheats_update();assert(!cheat.jetpack&&!synced[1]);
 return 0;}
'''
    (folder/"cheats.c").write_text(program)
    subprocess.run(["cc","-std=c99","-Wall","-Wextra","-Werror",str(folder/"cheats.c"),"-o",str(folder/"cheats")],check=True)
    subprocess.run([str(folder/"cheats")],check=True)
    print("Single-player cheat isolation and startup lifecycle checks passed.")


def test_network_helpers(folder):
    source = (ROOT / "port/linux/game/network_test.c").read_text()
    start=source.index("static boolean network_test_variant(")
    end=source.index("static void network_test_read_settings(",start)
    program = r'''#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef int boolean;
#define FALSE 0
#define TRUE 1
struct {char spec[256],map_name[128],variant_name[64];short spec_index,variant_index;} network_test;
''' + source[start:end] + r'''
int main(void) {
 char variant[64];strcpy(network_test.spec,"bloodgulch:slayer,ctf;hangemhigh:oddball");
 network_test_select_map();assert(network_test_has_next_game());
 assert(!strcmp(network_test.map_name,"bloodgulch"));assert(network_test_variant(0,variant,sizeof(variant))&&!strcmp(variant,"slayer"));
 network_test_next_game();assert(network_test_variant(network_test.variant_index,variant,sizeof(variant))&&!strcmp(variant,"ctf"));
 network_test_next_game();assert(!strcmp(network_test.map_name,"hangemhigh"));
 network_test_next_game();assert(!strcmp(network_test.map_name,"bloodgulch")&&network_test.variant_index==0);
 strcpy(network_test.spec,"levels\\a10\\a10:coop");network_test.spec_index=0;network_test_select_map();assert(!strcmp(network_test.map_name,"levels\\a10\\a10"));
 strcpy(network_test.spec,"bloodgulch");network_test_select_map();assert(!strcmp(network_test.variant_name,"slayer"));
 return 0;
}
'''
    (folder/"rotation.c").write_text(program)
    subprocess.run(["cc","-std=c99","-Wall","-Wextra","-Werror",str(folder/"rotation.c"),"-o",str(folder/"rotation")],check=True)
    subprocess.run([str(folder/"rotation")],check=True)
    source=(ROOT/"port/linux/src/p2p_signal.c").read_text()
    start=source.index("static void broker_publish(");end=source.index("/* a publish at least once",start)
    program=r'''#include <assert.h>
#include <string.h>
#define TOPIC_SIZE 64
#define P2P_RELAY_PACKET_SIZE 1536
struct broker {int protocol;};
static unsigned char sent[2048];static int count,size;
static int put_string(unsigned char *out,const char *s){int n=strlen(s);out[0]=n>>8;out[1]=n;memcpy(out+2,s,n);return n+2;}
static void broker_send(struct broker *b,unsigned char type,const unsigned char *body,int n){(void)b;assert(type==0x30);memcpy(sent,body,n);size=n;count++;}
'''+source[start:end]+r'''
int main(void){
 struct broker b={5};unsigned char payload[P2P_RELAY_PACKET_SIZE];memset(payload,0xab,sizeof(payload));
 broker_publish(&b,"hceu/r/test",payload,sizeof(payload));assert(count==1&&size==14+sizeof(payload));assert(sent[13]==0&&!memcmp(sent+14,payload,sizeof(payload)));
 broker_publish(&b,"hceu/r/test",payload,-1);broker_publish(&b,"hceu/r/test",payload,sizeof(payload)+1);assert(count==1);
 b.protocol=4;broker_publish(&b,"hceu/r/test",payload,sizeof(payload));assert(count==2&&size==13+sizeof(payload)&&!memcmp(sent+13,payload,sizeof(payload)));
 return 0;}
'''
    (folder/"relay.c").write_text(program)
    subprocess.run(["cc","-std=c99","-Wall","-Wextra","-Werror",str(folder/"relay.c"),"-o",str(folder/"relay")],check=True)
    subprocess.run([str(folder/"relay")],check=True)
    print("Server rotation and MQTT 3/5 relay packet bounds checks passed.")


def test_server_countdown(folder):
    source = (ROOT / "source/networking/network_server_manager.c").read_text()
    start = source.index("boolean server_has_enough_machines(")
    end = source.index("void network_game_server_invalidate_network_machine(", start)
    force_start = source.index("boolean network_game_server_port_force_start(")
    force_end = source.index("void network_game_server_port_log_state(", force_start)
    program = r'''#include <assert.h>
#include <stdarg.h>
typedef int boolean;
#define FALSE 0
#define TRUE 1
#define MAXIMUM_NETWORK_MACHINE_COUNT 4
#define _network_game_server_state_pregame 0
struct network_game_server_client_machine { int joined; };
struct network_game_server {
 struct { long player_count, minimum_players; } game;
 struct { int paused; } countdown_state;
 struct network_game_server_client_machine client_machines[4];
 int state;
};
static int players_on_each = 1, needs_teams, precached, starts;
static int network_game_server_client_machine_is_joined_to_game(struct network_game_server *s, struct network_game_server_client_machine *m) {(void)s;return m->joined;}
static int server_has_a_player_on_each_machine(struct network_game_server *s) {(void)s;return players_on_each;}
static int server_needs_more_teams(struct network_game_server *s) {(void)s;return needs_teams;}
static int network_game_server_have_all_machines_have_precached(struct network_game_server *s) {(void)s;return precached;}
static int network_game_server_start_network_game(struct network_game_server *s) {(void)s;starts++;return 1;}
static void network_event(const char *fmt, ...) {(void)fmt;}
''' + source[start:end] + source[force_start:force_end] + r'''
int main(void) {
 struct network_game_server s = {0};
 s.game.minimum_players = 2;
 assert(!server_ok_to_countdown(&s));
 s.client_machines[0].joined = 1; s.game.player_count = 1; needs_teams = 1;
 assert(server_ok_to_countdown(&s)); /* upstream permits a solo host */
 assert(!network_game_server_port_force_start(&s) && !starts);
 precached = 1;
 assert(network_game_server_port_force_start(&s) && starts == 1);
 players_on_each = 0;
 assert(!server_ok_to_countdown(&s));
 assert(!network_game_server_port_force_start(&s) && starts == 1);
 players_on_each = 1; s.game.player_count = 2;
 assert(!server_ok_to_countdown(&s)); /* multiple players still need teams */
 needs_teams = 0; s.game.minimum_players = 3;
 assert(!server_ok_to_countdown(&s));
 s.game.minimum_players = 2;
 assert(server_ok_to_countdown(&s));
 s.state = 1;
 assert(!network_game_server_port_force_start(&s));
 assert(!network_game_server_port_force_start(0));
 return 0;
}
'''
    (folder / "countdown.c").write_text(program)
    subprocess.run(["cc", "-std=c99", "-Wall", "-Wextra", "-Werror",
                    str(folder / "countdown.c"), "-o", str(folder / "countdown")], check=True)
    subprocess.run([str(folder / "countdown")], check=True)
    print("Solo-host countdown, team readiness and dedicated-server precache checks passed.")


def main():
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        test_singleplayer_cheats(folder)
        test_network_helpers(folder)
        test_server_countdown(folder)
        (folder / "MobileCheck.java").write_text(JAVA_TEST)
        javac = ["javac"] if shutil.which("javac") else ["java", "-m", "jdk.compiler/com.sun.tools.javac.Main"]
        subprocess.run([*javac,"-d",str(folder),*[str(JAVA / (name+".java")) for name in
            ["TouchConfiguration","GyroscopeAim","StartupCheats","XisoExtractor"]],str(folder / "MobileCheck.java")],check=True)
        subprocess.run(["java","-cp",str(folder),"com.halo.decomp.MobileCheck",str(folder)],check=True)
        homes = [Path(os.environ.get("JAVA_HOME","/nonexistent")),Path(shutil.which("java")).resolve().parents[1],ROOT/"build/integration/jdk"]
        include = next((home/"include" for home in homes if (home/"include/jni.h").is_file()),None)
        if include is None: raise RuntimeError("A JDK with JNI headers is required for native checks")
        (folder / "mobile.c").write_text(C_TEST)
        subprocess.run(["cc","-std=c11","-D_POSIX_C_SOURCE=200809L","-Wall","-Wextra","-Werror",
            "-I",str(ROOT),"-I",str(include),"-I",str(include/"linux"),"-I",str(ROOT/"port/android/include"),
            str(folder/"mobile.c"),"-pthread","-o",str(folder/"mobile")],check=True)
        subprocess.run([str(folder/"mobile")],check=True)
        print("Native movie lifecycle, language fallback and mobile bridge checks passed.")

if __name__ == "__main__": main()
