package com.halo.decomp;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.SharedPreferences;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.graphics.RectF;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.LinearLayout;
import android.widget.SeekBar;
import android.widget.Spinner;
import android.widget.TextView;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.libsdl.app.SDLActivity;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/** Editable multitouch gamepad with relative swipe aim and absolute menu taps. */
public final class TouchControls extends View {
    private static final int BUTTON = 0, MOVE = 1, AIM = 2;
    private static final int PAD = 1000;
    private static final String[] ACTION_NAMES = {
        "A / select / jump", "B / cancel / melee", "X / use / reload", "Y / switch weapon",
        "LB / flashlight", "LT / grenade", "RB / switch grenade", "RT / fire",
        "L3 / crouch", "R3 / zoom", "START / pause / finish name", "BACK / scoreboard",
        "D-pad up", "D-pad down", "D-pad left", "D-pad right", "None"
    };
    private static final int[] ACTION_KEYS = {
        PAD, PAD+1, PAD+2, PAD+3, PAD+9, PAD+15, PAD+10, PAD+16,
        PAD+7, PAD+8, PAD+6, PAD+4, PAD+11, PAD+12, PAD+13, PAD+14, 0
    };

    private static final class Control {
        String id, label;
        int kind, action, pressed;
        float x, y, radius, opacity;
        Control(String id, String label, int kind, int action, float x, float y, float radius) {
            this.id = id; this.label = label; this.kind = kind; this.action = action;
            this.x = x; this.y = y; this.radius = radius; opacity = 0.45f;
        }
    }
    private static final class Finger {
        Control control;
        int action;
        float downX, downY, lastX, lastY, startX, startY;
        boolean dragged, menu;
    }

    private final Activity activity;
    private final SharedPreferences prefs;
    private final ArrayList<Control> controls = new ArrayList<>();
    private final Map<Integer, Finger> fingers = new HashMap<>();
    private final Map<Integer, Integer> held = new HashMap<>();
    private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final RectF editRect = new RectF(), menuRect = new RectF(), optionsRect = new RectF();
    private boolean editing, menuTouch = true, menus = true;
    private int inputMode = -1;
    private float pointerX, pointerY;
    private final Runnable modePoll = new Runnable() {
        @Override public void run() {
            refreshMode();
            postDelayed(this, 100);
        }
    };
    private int toolbarPointer = -1, toolbarAction = -1, mouseState;
    private float sensitivity = 1.8f;

    public TouchControls(Activity activity) {
        super(activity);
        this.activity = activity;
        prefs = activity.getSharedPreferences("touch_controls_v3", Activity.MODE_PRIVATE);
        setFocusable(false);
        setClickable(true);
        defaults();
        load();
    }

    @Override protected void onAttachedToWindow() {
        super.onAttachedToWindow();
        post(modePoll);
    }
    @Override protected void onDetachedFromWindow() {
        removeCallbacks(modePoll);
        releaseAll();
        super.onDetachedFromWindow();
    }
    private void refreshMode() {
        int mode = TouchInput.mode();
        if (mode == inputMode) return;
        releaseAll();
        boolean nextMenus = (mode & 1) != 0;
        if (nextMenus != menus) {
            editing = false;
            menuTouch = nextMenus;
        }
        menus = nextMenus;
        inputMode = mode;
        invalidate();
    }

    private float dp(float value) { return value * getResources().getDisplayMetrics().density; }
    private float unit() { return Math.min(getWidth(), getHeight()); }
    private float radius(Control c) { return Math.max(dp(18), c.radius * unit()); }
    private static float clamp(float x, float lo, float hi) { return Math.max(lo, Math.min(hi, x)); }
    private void add(String id, String label, int kind, int action, float x, float y, float r) {
        controls.add(new Control(id, label, kind, action, x, y, r));
    }
    private void defaults() {
        controls.clear();
        add("move", "MOVE", MOVE, 0, .14f, .72f, .16f);
        add("aim", "AIM", AIM, 0, .59f, .68f, .18f);
        add("a", "A", BUTTON, PAD, .87f, .73f, .065f);
        add("b", "B", BUTTON, PAD+1, .95f, .62f, .065f);
        add("x", "X", BUTTON, PAD+2, .79f, .62f, .065f);
        add("y", "Y", BUTTON, PAD+3, .87f, .51f, .065f);
        add("lb", "LB", BUTTON, PAD+9, .08f, .24f, .055f);
        add("lt", "LT", BUTTON, PAD+15, .19f, .24f, .055f);
        add("rb", "RB", BUTTON, PAD+10, .83f, .24f, .055f);
        add("rt", "RT", BUTTON, PAD+16, .94f, .24f, .07f);
        add("l3", "L3", BUTTON, PAD+7, .29f, .48f, .05f);
        add("r3", "R3", BUTTON, PAD+8, .73f, .42f, .05f);
        add("start", "START", BUTTON, PAD+6, .58f, .24f, .055f);
        add("back", "BACK", BUTTON, PAD+4, .47f, .24f, .055f);
        add("reload", "RELOAD", BUTTON, PAD+2, .75f, .89f, .06f);
        add("score", "SCORE", BUTTON, PAD+4, .36f, .24f, .055f);
        add("up", "UP", BUTTON, PAD+11, .36f, .65f, .04f);
        add("down", "DOWN", BUTTON, PAD+12, .36f, .87f, .04f);
        add("left", "LEFT", BUTTON, PAD+13, .305f, .76f, .04f);
        add("right", "RIGHT", BUTTON, PAD+14, .415f, .76f, .04f);
    }

    private void load() {
        sensitivity = clamp(prefs.getFloat("sensitivity", 1.8f), .25f, 5f);
        try {
            String saved = prefs.getString("layout", "");
            boolean legacy = saved.isEmpty();
            if (legacy) {
                SharedPreferences old = activity.getSharedPreferences("touch_controls_v2", Activity.MODE_PRIVATE);
                saved = old.getString("layout", "");
                sensitivity = clamp(old.getFloat("sensitivity", sensitivity), .25f, 5f);
            }
            if (saved.isEmpty()) return;
            JSONArray array = new JSONArray(saved);
            ArrayList<Control> loaded = new ArrayList<>();
            for (int i = 0; i < array.length(); i++) {
                JSONObject o = array.getJSONObject(i);
                int kind = o.getInt("kind"), action = o.getInt("action");
                if (legacy) action = migrateAction(action);
                if (kind < BUTTON || kind > AIM || !validAction(action)) throw new JSONException("Invalid control");
                Control c = new Control(o.getString("id"), o.getString("label"), kind, action,
                        clamp((float)o.getDouble("x"), 0, 1), clamp((float)o.getDouble("y"), 0, 1),
                        clamp((float)o.getDouble("radius"), .025f, .3f));
                c.opacity = clamp((float)o.getDouble("opacity"), .1f, .9f);
                loaded.add(c);
            }
            if (!loaded.isEmpty()) { controls.clear(); controls.addAll(loaded); }
        } catch (JSONException | ClassCastException ignored) { defaults(); }
    }

    private int migrateAction(int key) {
        switch (key) {
            case KeyEvent.KEYCODE_SPACE: case KeyEvent.KEYCODE_ENTER: return PAD;
            case KeyEvent.KEYCODE_F: return PAD+1;
            case KeyEvent.KEYCODE_E: case KeyEvent.KEYCODE_R: case KeyEvent.KEYCODE_FORWARD_DEL: return PAD+2;
            case KeyEvent.KEYCODE_1: return PAD+3;
            case KeyEvent.KEYCODE_Q: return PAD+9;
            case KeyEvent.KEYCODE_G: case -2: return PAD+15;
            case KeyEvent.KEYCODE_X: return PAD+10;
            case -1: return PAD+16;
            case KeyEvent.KEYCODE_CTRL_LEFT: return PAD+7;
            case KeyEvent.KEYCODE_Z: case -4: return PAD+8;
            case KeyEvent.KEYCODE_ESCAPE: return PAD+6;
            case KeyEvent.KEYCODE_DEL: case KeyEvent.KEYCODE_TAB: return PAD+4;
            case KeyEvent.KEYCODE_DPAD_UP: return PAD+11;
            case KeyEvent.KEYCODE_DPAD_DOWN: return PAD+12;
            case KeyEvent.KEYCODE_DPAD_LEFT: return PAD+13;
            case KeyEvent.KEYCODE_DPAD_RIGHT: return PAD+14;
            default: return 0;
        }
    }

    private boolean validAction(int action) {
        for (int key : ACTION_KEYS) if (key == action) return true;
        return false;
    }
    private void save() {
        JSONArray array = new JSONArray();
        try {
            for (Control c : controls) {
                JSONObject o = new JSONObject();
                o.put("id", c.id).put("label", c.label).put("kind", c.kind).put("action", c.action)
                        .put("x", c.x).put("y", c.y).put("radius", c.radius).put("opacity", c.opacity);
                array.put(o);
            }
            prefs.edit().putString("layout", array.toString()).putFloat("sensitivity", sensitivity).apply();
        } catch (JSONException ignored) { /* Only finite values enter this layout. */ }
    }

    @Override protected void onSizeChanged(int w, int h, int oldw, int oldh) {
        releaseAll();
        float top = dp(8), height = dp(34), width = dp(72), gap = dp(8);
        float left = Math.max(dp(8), (w - 3 * width - 2 * gap) / 2f);
        editRect.set(left, top, left + width, top + height);
        menuRect.set(editRect.right + gap, top, editRect.right + gap + width, top + height);
        optionsRect.set(menuRect.right + gap, top, menuRect.right + gap + width, top + height);
        for (Control c : controls) bound(c);
    }
    private void bound(Control c) {
        if (getWidth() == 0 || getHeight() == 0) return;
        float r = radius(c);
        c.x = clamp(c.x, r / getWidth(), 1 - r / getWidth());
        c.y = clamp(c.y, (editRect.bottom + dp(8) + r) / getHeight(), 1 - r / getHeight());
    }

    @Override protected void onDraw(Canvas canvas) {
        if (!menuTouch || editing) {
            for (Control c : controls) {
                float x = c.x * getWidth(), y = c.y * getHeight(), r = radius(c);
                paint.setStyle(Paint.Style.FILL);
                paint.setColor(c.pressed > 0 ? 0xFF3E98B5 : 0xFF203342);
                paint.setAlpha((int)(255 * (editing ? .7f : c.opacity)));
                canvas.drawCircle(x, y, r, paint);
                paint.setStyle(Paint.Style.STROKE); paint.setStrokeWidth(dp(1.5f));
                paint.setColor(Color.WHITE); paint.setAlpha(editing ? 210 : 135);
                canvas.drawCircle(x, y, r, paint);
                if (c.kind != BUTTON) {
                    paint.setAlpha(100);
                    canvas.drawCircle(x, y, r * .4f, paint);
                    for (Finger f : fingers.values()) {
                        if (f.control == c && !editing) {
                            float dx = f.lastX - f.downX, dy = f.lastY - f.downY;
                            float length = (float)Math.hypot(dx, dy), scale = length > r * .6f ? r * .6f / length : 1;
                            canvas.drawCircle(x + dx * scale, y + dy * scale, r * .25f, paint);
                        }
                    }
                }
                paint.setStyle(Paint.Style.FILL); paint.setColor(Color.WHITE); paint.setAlpha(235);
                paint.setTextAlign(Paint.Align.CENTER);
                paint.setTextSize(Math.min(dp(13), r * .35f));
                canvas.drawText(c.label, x, y - (paint.ascent() + paint.descent()) / 2, paint);
            }
        }
        toolbar(canvas, editRect, editing ? "DONE" : "EDIT");
        toolbar(canvas, menuRect, menus ? (menuTouch ? "PAD" : "TOUCH") : (menuTouch ? "GAME" : "MENU"));
        toolbar(canvas, optionsRect, "OPTIONS");
        if (menuTouch && !editing) {
            paint.setColor(Color.WHITE); paint.setAlpha(230); paint.setTextSize(dp(12));
            paint.setTextAlign(Paint.Align.CENTER);
            canvas.drawText((inputMode & 2) != 0 ? "Tap letters, then DONE. PAD offers controller buttons." : "Tap menu items. PAD offers controller buttons.", getWidth()/2f, editRect.bottom + dp(18), paint);
        }
        if (editing) {
            paint.setColor(Color.WHITE); paint.setAlpha(230); paint.setTextSize(dp(12));
            paint.setTextAlign(Paint.Align.CENTER);
            canvas.drawText("Drag to move. Tap to change size, opacity or action.", getWidth()/2f, editRect.bottom + dp(18), paint);
        }
    }
    private void toolbar(Canvas canvas, RectF rect, String text) {
        paint.setStyle(Paint.Style.FILL); paint.setColor(0xD9203342);
        canvas.drawRoundRect(rect, dp(6), dp(6), paint);
        paint.setColor(Color.WHITE); paint.setTextAlign(Paint.Align.CENTER); paint.setTextSize(dp(12));
        canvas.drawText(text, rect.centerX(), rect.centerY() - (paint.ascent() + paint.descent()) / 2, paint);
    }
    private int toolbarAt(float x, float y) {
        if (editRect.contains(x,y)) return 0;
        if (menuRect.contains(x,y)) return 1;
        if (optionsRect.contains(x,y)) return 2;
        return -1;
    }
    private Control hit(float x, float y) {
        // Buttons take precedence over pads when an edited layout overlaps.
        for (int pass = 0; pass < 2; pass++)
            for (int i = controls.size()-1; i >= 0; i--) {
                Control c = controls.get(i);
                if ((c.kind == BUTTON) != (pass == 0)) continue;
                if (Math.hypot(x-c.x*getWidth(), y-c.y*getHeight()) <= radius(c)) return c;
            }
        return null;
    }

    @Override public boolean onTouchEvent(MotionEvent e) {
        refreshMode();
        if ((inputMode & 4) == 0) return true;
        int action = e.getActionMasked(), index = e.getActionIndex(), id = e.getPointerId(index);
        if (action == MotionEvent.ACTION_CANCEL) { releaseAll(); return true; }
        if (action == MotionEvent.ACTION_DOWN || action == MotionEvent.ACTION_POINTER_DOWN) {
            float x = e.getX(index), y = e.getY(index);
            int tool = toolbarAt(x,y);
            if (tool >= 0 && fingers.isEmpty() && toolbarPointer < 0) {
                toolbarPointer = id; toolbarAction = tool; return true;
            }
            if (toolbarPointer >= 0) return true;
            Control c = editing || !menuTouch ? hit(x,y) : null;
            if (c == null && (!menuTouch || editing)) return true;
            // Each stick has one owner; additional fingers cannot steal it.
            for (Finger other : fingers.values())
                if (editing || menuTouch || (c != null && c.kind != BUTTON && other.control == c)) return true;
            Finger f = new Finger(); f.control = c;
            f.downX = f.lastX = x; f.downY = f.lastY = y;
            if (c != null) { f.startX = c.x; f.startY = c.y; f.action = c.action; c.pressed++; }
            f.menu = menuTouch && !editing;
            fingers.put(id, f);
            if (!editing) {
                if (f.menu) menuMouse(x, y, MotionEvent.ACTION_DOWN);
                else if (c.kind == BUTTON) hold(f.action,true);
            }
        } else if (action == MotionEvent.ACTION_MOVE) {
            for (int i = 0; i < e.getPointerCount(); i++) {
                Finger f = fingers.get(e.getPointerId(i));
                if (f == null) continue;
                float x = e.getX(i), y = e.getY(i), dx = x-f.lastX, dy = y-f.lastY;
                if (editing) {
                    if (Math.hypot(x-f.downX,y-f.downY) > dp(8)) f.dragged = true;
                    if (f.dragged) {
                        f.control.x = f.startX + (x-f.downX)/getWidth();
                        f.control.y = f.startY + (y-f.downY)/getHeight(); bound(f.control);
                    }
                } else if (f.menu) menuMouse(x, y, MotionEvent.ACTION_MOVE);
                else if (f.control.kind == AIM) mouseMove(dx*sensitivity,dy*sensitivity,true);
                else if (f.control.kind == MOVE) {
                    float r = radius(f.control), mx = (x-f.downX)/r, my = (y-f.downY)/r;
                    float length = (float)Math.hypot(mx, my);
                    if (length < .15f) { mx = my = 0; }
                    else if (length > 1) { mx /= length; my /= length; }
                    TouchInput.move(mx, my);
                }
                f.lastX = x; f.lastY = y;
            }
        } else if (action == MotionEvent.ACTION_UP || action == MotionEvent.ACTION_POINTER_UP) {
            if (id == toolbarPointer) {
                int tool = toolbarAction; toolbarPointer = toolbarAction = -1;
                if (toolbarAt(e.getX(index),e.getY(index)) == tool) {
                    releaseAll();
                    if (tool == 0) { editing = !editing; if (editing) menuTouch = false; save(); }
                    if (tool == 1) {
                        editing = false;
                        menuTouch = !menuTouch;
                        if (!menus && menuTouch) {
                            TouchInput.button(6, true); TouchInput.button(6, false);
                        }
                    }
                    if (tool == 2) options();
                }
            } else {
                Finger f = fingers.remove(id);
                if (f != null) {
                    if (f.control != null) f.control.pressed = Math.max(0,f.control.pressed-1);
                    if (editing) { save(); if (!f.dragged) editControl(f.control); }
                    else if (f.menu) menuMouse(e.getX(index), e.getY(index), MotionEvent.ACTION_UP);
                    else if (f.control.kind == BUTTON) hold(f.action,false);
                    else if (f.control.kind == MOVE) TouchInput.move(0,0);
                }
            }
        }
        invalidate(); return true;
    }

    private void mouseMove(float x, float y, boolean relative) {
        SDLActivity.onNativeMouse(0, MotionEvent.ACTION_MOVE, x, y, relative);
    }
    private void menuMouse(float x, float y, int action) {
        pointerX = x; pointerY = y;
        if (action == MotionEvent.ACTION_DOWN) mouseState = 1;
        if (action == MotionEvent.ACTION_UP) mouseState = 0;
        // Both edges carry the clicked position; never send a relative zero
        // movement in menu mode or click at the old mouse position.
        SDLActivity.onNativeMouse(mouseState, action, x, y, false);
    }
    private void hold(int action, boolean down) {
        if (action == 0) return;
        int count = held.containsKey(action) ? held.get(action) : 0;
        if (!down && count == 0) return;
        int next = down ? count+1 : count-1;
        if (next == 0) held.remove(action); else held.put(action,next);
        if ((count == 0 && down) || (next == 0 && !down)) {
            TouchInput.button(action - PAD, down);
        }
    }
    public void releaseAll() {
        TouchInput.reset();
        held.clear();
        if (mouseState != 0) menuMouse(pointerX, pointerY, MotionEvent.ACTION_UP);
        fingers.clear(); toolbarPointer = toolbarAction = -1;
        for (Control c : controls) c.pressed = 0;
        invalidate();
    }

    private LinearLayout dialogLayout() {
        LinearLayout layout = new LinearLayout(activity); layout.setOrientation(LinearLayout.VERTICAL);
        int padding = (int)dp(20); layout.setPadding(padding,padding,padding,padding); return layout;
    }
    private SeekBar slider(LinearLayout layout, String title, int max, int progress) {
        TextView label = new TextView(activity); label.setText(title); layout.addView(label);
        SeekBar seek = new SeekBar(activity); seek.setMax(max); seek.setProgress(progress); layout.addView(seek); return seek;
    }
    private int actionIndex(int key) {
        for (int i = 0; i < ACTION_KEYS.length; i++) if (ACTION_KEYS[i] == key) return i;
        return ACTION_KEYS.length - 1;
    }
    private void editControl(Control c) {
        releaseAll();
        LinearLayout layout = dialogLayout();
        Spinner action = new Spinner(activity);
        if (c.kind == BUTTON) {
            action.setAdapter(new ArrayAdapter<>(activity,android.R.layout.simple_spinner_dropdown_item,ACTION_NAMES));
            action.setSelection(actionIndex(c.action)); layout.addView(action);
        }
        SeekBar size = slider(layout,"Size",275,Math.round(c.radius*1000)-25);
        SeekBar opacity = slider(layout,"Opacity",80,Math.round(c.opacity*100)-10);
        new AlertDialog.Builder(activity).setTitle(c.label).setView(layout)
            .setPositiveButton("Save",(d,w)->{
                if (c.kind == BUTTON) {
                    c.action = ACTION_KEYS[action.getSelectedItemPosition()];
                    // Keep familiar default labels, show the chosen action on custom buttons.
                    if (c.id.startsWith("custom")) c.label = ACTION_NAMES[action.getSelectedItemPosition()].split(" / ")[0];
                }
                c.radius = (size.getProgress()+25)/1000f; c.opacity = (opacity.getProgress()+10)/100f;
                bound(c); save(); invalidate();
            }).setNegativeButton("Cancel",null)
            .setNeutralButton("Remove",(d,w)->{controls.remove(c); save(); invalidate();}).show();
    }
    private void options() {
        releaseAll();
        String[] choices = {"Aim sensitivity", "Add button", "Reset layout", "Help"};
        new AlertDialog.Builder(activity).setTitle("Touch controls").setItems(choices,(d,which)->{
            if (which == 0) {
                LinearLayout layout = dialogLayout();
                SeekBar value = slider(layout,"Aim sensitivity (0.25 to 5)",475,Math.round(sensitivity*100)-25);
                new AlertDialog.Builder(activity).setTitle("Aim sensitivity").setView(layout)
                    .setPositiveButton("Save",(a,b)->{sensitivity=(value.getProgress()+25)/100f;save();})
                    .setNegativeButton("Cancel",null).show();
            } else if (which == 1) {
                editing = true; menuTouch = false;
                add("custom"+System.nanoTime(),"NEW",BUTTON,PAD,.5f,.5f,.065f);
                save(); invalidate(); editControl(controls.get(controls.size()-1));
            } else if (which == 2) {
                new AlertDialog.Builder(activity).setMessage("Restore the default touchscreen layout and button actions?")
                    .setPositiveButton("Reset",(a,b)->{defaults(); for(Control c:controls)bound(c);save();invalidate();})
                    .setNegativeButton("Cancel",null).show();
            } else new AlertDialog.Builder(activity).setTitle("How to play")
                .setMessage("MOVE: slide for analog movement. AIM: swipe to look. You can move, aim and hold fire together.\n\nMenus automatically use direct taps, including the profile keyboard. Tap letters and DONE to save your name. PAD shows controller buttons: arrows move, A selects, B cancels, X deletes and START finishes the name. TOUCH returns to tapping. In gameplay, MENU opens pause.\n\nEDIT: drag any control to move it. Tap a control to change its size, opacity and button action, or remove it. DONE saves the layout. OPTIONS lets you add buttons, reset the layout or change aim sensitivity.\n\nThe buttons are a gamepad, so they cannot type keyboard letters accidentally. Gameplay actions follow your controller profile.")
                .setPositiveButton("OK",null).show();
        }).show();
    }
}

