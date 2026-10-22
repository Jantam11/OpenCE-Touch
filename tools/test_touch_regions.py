#!/usr/bin/env python3
"""Exercise the production Android event router with synthetic multitouch events.

Only Android/SDL services are stubbed. Button hit testing, mode changes,
ownership, movement/look dispatch and cancellation come from TouchControls.java.
Phone gameplay and a complete Android build remain separate checks.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "port/android/app/src/main/java/com/halo/decomp"


def method(source, signature):
    start = source.index(signature)
    body = source.index("{", start)
    depth = 1
    end = body + 1
    while depth:
        depth += (source[end] == "{") - (source[end] == "}")
        end += 1
    return source[start:end]


STUBS = r'''
package com.halo.decomp;
import java.util.*;
class MotionEvent {
 static final int ACTION_DOWN=0,ACTION_UP=1,ACTION_MOVE=2,ACTION_CANCEL=3,ACTION_POINTER_DOWN=5,ACTION_POINTER_UP=6;
 int action,index;int[] ids;float[] xs,ys;
 MotionEvent(int a,int index,int[] ids,float[] xs,float[] ys){action=a;this.index=index;this.ids=ids;this.xs=xs;this.ys=ys;}
 int getActionMasked(){return action;}int getActionIndex(){return index;}int getPointerId(int i){return ids[i];}
 int getPointerCount(){return ids.length;}float getX(int i){return xs[i];}float getY(int i){return ys[i];}
 float getX(){return xs[0];}float getY(){return ys[0];}
}
class View {public boolean onTouchEvent(MotionEvent e){return false;}}
class TouchInput {
 static int currentMode=4;static float x,y;static Set<Integer> held=new HashSet<>();
 static int mode(){return currentMode;}static void reset(){x=y=0;held.clear();}
 static void move(float a,float b){x=a;y=b;}
 static void button(int b,boolean down){if(down)held.add(b);else held.remove(b);}
}
class SDLActivity {
 static float x,y;static int lookEvents,menuEvents,mouseHeld;
 static void onNativeMouse(int button,int action,float a,float b,boolean relative){
  if(relative){x+=a;y+=b;lookEvents++;}else{menuEvents++;mouseHeld=button;}
 }
 static void reset(){x=y=0;lookEvents=menuEvents=mouseHeld=0;}
}
public class RegionRoutingCheck extends View {
 static final int BUTTON=0,MOVE=1,AIM=2,PAD=1000,CAMERA=2000;
 private static final class Control {
  String id,label;int kind,action,pressed;float x,y,radius,opacity;
  Control(int kind,int action,float x,float y,float radius){this.kind=kind;this.action=action;this.x=x;this.y=y;this.radius=radius;}
 }
 private static final class Finger {
  Control control;int action,region;float downX,downY,lastX,lastY,startX,startY;boolean dragged,menu;
 }
 private final ArrayList<Control> controls=new ArrayList<>();
 private final Map<Integer,Finger> fingers=new HashMap<>();
 private final Map<Integer,Integer> held=new HashMap<>();
 private final TouchRegions regions=new TouchRegions();
 private final TouchConfiguration settings=new TouchConfiguration();
 private final GyroscopeAim gyroAim=new GyroscopeAim();
 private boolean editing,menuTouch,menus,hudEditing,movieActive;
 private int inputMode=4,toolbarPointer=-1,toolbarAction=-1,mouseState;
 private float sensitivity=1.8f,pointerX,pointerY;
 int getWidth(){return 1000;}int getHeight(){return 500;}float dp(float n){return n;}
 float radius(Control c){return c.radius*500;}
 int toolbarAt(float x,float y){return y<30?2:-1;}
 void invalidate(){}void updateSensors(){}void save(){}void options(){}
 boolean hudTouch(MotionEvent e){return true;}void bound(Control c){}void editControl(Control c){}
 void nativeLookReset(){SDLActivity.x=SDLActivity.y=0;}void nativeCameraMode(){}
'''

CASES = r'''
 static void check(boolean ok){if(!ok)throw new AssertionError();}
 static void near(float a,float b){check(Math.abs(a-b)<.001f);}
 void event(int action,int index,int[] ids,float... xy){
  float[] xs=new float[ids.length],ys=new float[ids.length];
  for(int i=0;i<ids.length;i++){xs[i]=xy[2*i];ys[i]=xy[2*i+1];}
  onTouchEvent(new MotionEvent(action,index,ids,xs,ys));
 }
 static RegionRoutingCheck game(boolean regions){
  TouchInput.currentMode=4;SDLActivity.reset();TouchInput.reset();
  RegionRoutingCheck v=new RegionRoutingCheck();v.settings.screenRegions=regions;
  v.controls.add(new Control(MOVE,0,.14f,.72f,.16f));
  v.controls.add(new Control(AIM,0,.59f,.68f,.18f));
  v.controls.add(new Control(BUTTON,1016,.9f,.5f,.07f));
  v.controls.add(new Control(BUTTON,1000,.12f,.5f,.07f));
  return v;
 }
 public static void main(String[] args){
  // The classic hit areas stay active by default; empty space does nothing.
  RegionRoutingCheck v=game(false);
  v.event(0,0,new int[]{0},300,150);check(v.fingers.isEmpty());
  v.event(0,0,new int[]{0},140,360);v.event(2,0,new int[]{0},180,360);near(TouchInput.x,.5f);
  v.event(1,0,new int[]{0},180,360);near(TouchInput.x,0);
  v.event(0,0,new int[]{0},590,340);v.event(2,0,new int[]{0},600,345);near(SDLActivity.x,18);near(SDLActivity.y,9);v.releaseAll();
  // Region capture ignores hidden pads and gives buttons priority.
  v=game(true);v.event(0,0,new int[]{17},140,360);
  v.event(5,1,new int[]{17,29},140,360,700,300);
  v.event(5,2,new int[]{17,29,35},140,360,700,300,900,250);
  check(TouchInput.held.contains(16));check(v.fingers.size()==3);
  // Android can reorder pointer indices: identity, not index, owns a region.
  v.event(2,0,new int[]{29,35,17},710,305,900,250,170,345);
  near(TouchInput.x,.5f);near(TouchInput.y,-.5f);near(SDLActivity.x,18);near(SDLActivity.y,9);
  check(SDLActivity.lookEvents==2); // region look and existing fire-drag path (zero delta)
  v.event(5,3,new int[]{29,35,17,41},710,305,900,250,170,345,300,300);check(v.fingers.size()==3);
  v.event(6,1,new int[]{29,35,17},710,305,900,250,170,345);
  check(!TouchInput.held.contains(16));near(TouchInput.x,.5f);
  v.event(2,0,new int[]{29,17},400,305,700,345);near(TouchInput.x,1);near(SDLActivity.x,-540);
  v.event(6,0,new int[]{29,17},400,305,700,345);near(TouchInput.x,1);
  v.event(1,0,new int[]{17},700,345);near(TouchInput.x,0);check(v.fingers.isEmpty());
  v.event(0,0,new int[]{0},120,250);check(TouchInput.held.contains(0));near(TouchInput.x,0);
  v.event(3,0,new int[]{0},120,250);check(TouchInput.held.isEmpty());
  // CANCEL releases held movement/fire; stale moves cannot restart either.
  v.event(0,0,new int[]{1},200,200);v.event(5,1,new int[]{1,2},200,200,900,250);
  v.event(2,0,new int[]{1,2},260,200,900,250);near(TouchInput.x,1);
  v.event(3,0,new int[]{1,2},260,200,900,250);near(TouchInput.x,0);check(TouchInput.held.isEmpty());
  v.event(2,0,new int[]{1},300,200);near(TouchInput.x,0);
  // A native menu/profile or chat transition clears gameplay before absolute taps.
  v.event(0,0,new int[]{1},200,200);v.event(2,0,new int[]{1},260,200);
  TouchInput.currentMode=7;v.event(0,0,new int[]{3},300,200);near(TouchInput.x,0);
  check(v.menus&&v.menuTouch&&SDLActivity.mouseHeld==1);
  v.event(1,0,new int[]{3},300,200);check(SDLActivity.mouseHeld==0);
  v.menuTouch=false;check(!v.useRegions()); // menu PAD still uses classic controls
  v.event(0,0,new int[]{3},140,360);check(v.fingers.get(3).control.kind==MOVE);v.releaseAll();
  TouchInput.currentMode=12;v.event(0,0,new int[]{4},300,200);check(SDLActivity.mouseHeld==1);check(v.fingers.isEmpty());
  v.event(3,0,new int[]{4},300,200);check(SDLActivity.mouseHeld==0);
  // Editor, disabled overlay and movie playback never capture gameplay regions.
  v=game(true);v.editing=true;v.event(0,0,new int[]{1},140,360);check(v.fingers.get(1).control.kind==MOVE);v.releaseAll();
  v.editing=false;v.settings.overlayDisabled=true;v.event(0,0,new int[]{1},200,200);check(v.fingers.isEmpty());
  v.settings.overlayDisabled=false;v.movieActive=true;v.event(0,0,new int[]{1},200,200);check(v.fingers.isEmpty());
  v.movieActive=false;v.event(0,0,new int[]{1},500,10);check(v.fingers.isEmpty()&&v.toolbarPointer==1);
  System.out.println("Production touch routing: classic/regions, buttons, pointer order, cancel, menus, chat and editor passed.");
 }
}
'''


def main():
    source = (JAVA / "TouchControls.java").read_text()
    functions = [method(source, signature) for signature in [
        "private void refreshMode()", "private boolean useRegions()", "private Control hit(",
        "@Override public boolean onTouchEvent(", "private void mouseMove(",
        "private void menuMouse(", "private void hold(", "public void releaseAll()",
    ]]
    with tempfile.TemporaryDirectory() as directory:
        folder = Path(directory)
        harness = folder / "RegionRoutingCheck.java"
        harness.write_text(STUBS + "\n".join(functions) + CASES)
        javac = ["javac"] if shutil.which("javac") else ["java", "-m", "jdk.compiler/com.sun.tools.javac.Main"]
        subprocess.run([*javac, "--release", "17", "-d", str(folder),
                        str(JAVA / "TouchRegions.java"), str(JAVA / "TouchConfiguration.java"),
                        str(JAVA / "GyroscopeAim.java"), str(harness)], check=True)
        subprocess.run(["java", "-cp", str(folder), "com.halo.decomp.RegionRoutingCheck"], check=True)


if __name__ == "__main__":
    main()
