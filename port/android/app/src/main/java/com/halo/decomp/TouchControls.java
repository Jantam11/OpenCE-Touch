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
public final class TouchControls extends View implements android.hardware.SensorEventListener {
    private static final int BUTTON = 0, MOVE = 1, AIM = 2;
    private static final int PAD = 1000, CAMERA = 2000;
    private static final String[] ACTION_NAMES = {
        "A / select / jump", "B / cancel / melee", "X / use / reload", "Y / switch weapon",
        "LB / flashlight", "LT / grenade", "RB / switch grenade", "RT / fire",
        "L3 / crouch", "R3 / zoom", "START / pause / finish name", "BACK / scoreboard",
        "D-pad up", "D-pad down", "D-pad left", "D-pad right", "Camera mode", "None"
    };
    private static final int[] ACTION_KEYS = {
        PAD, PAD+1, PAD+2, PAD+3, PAD+9, PAD+15, PAD+10, PAD+16,
        PAD+7, PAD+8, PAD+6, PAD+4, PAD+11, PAD+12, PAD+13, PAD+14, CAMERA, 0
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
            pollFeatures();
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
        loadFeatures();
    }

    @Override protected void onAttachedToWindow() {
        super.onAttachedToWindow();
        post(modePoll);
    }
    @Override protected void onDetachedFromWindow() {
        removeCallbacks(modePoll);
        stopDeviceInput();
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
        updateSensors();
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
        if (movieActive) return;
        if (settings.fps && !menus && !editing && !settings.overlayDisabled) {
            paint.setColor(Color.WHITE); paint.setAlpha(255); paint.setTextSize(dp(14));
            paint.setTextAlign(Paint.Align.LEFT); canvas.drawText("FPS: " + currentFps, dp(12), dp(70), paint);
        }
        if (settings.overlayDisabled && !editing) return;
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
                if (settings.icons && c.kind == BUTTON) {
                    int icon = iconFor(c.action);
                    if (icon >= 0) TouchIcons.draw(canvas, paint, icon, x, y, r*.68f, c.pressed > 0);
                    else canvas.drawText(c.label, x, y - (paint.ascent() + paint.descent()) / 2, paint);
                } else canvas.drawText(c.label, x, y - (paint.ascent() + paint.descent()) / 2, paint);
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
        if ((inputMode & 4) == 0 || movieActive) return true;
        if (settings.overlayDisabled && !editing) {
            int a = e.getActionMasked();
            if (menus) menuMouse(e.getX(), e.getY(), a);
            return true;
        }
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
                else if (f.control.kind == AIM || f.control.kind == BUTTON && f.action == PAD+16)
                    mouseMove(dx*sensitivity,dy*sensitivity,true);
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
        if (action == CAMERA) { if (down && !menus) nativeCameraMode(); return; }
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
        gyroAim.reset();
        nativeLookReset();
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
    public void options() {
        releaseAll();
        String[] choices = {"Aim sensitivity", "Add button", "Reset layout", "Help", "General settings", "Export layout", "Import layout", "Single-player cheats", "Import disc movies", "Camera mode", "Layout presets"};
        new AlertDialog.Builder(activity).setTitle("Touch controls").setItems(choices,(d,which)->{
            if (which == 0) {
                LinearLayout layout = dialogLayout();
                SeekBar value = slider(layout,"Aim sensitivity (0.25 to 5)",475,Math.round(sensitivity*100)-25);
                new AlertDialog.Builder(activity).setTitle("Aim sensitivity").setView(layout)
                    .setPositiveButton("Save",(a,b)->{sensitivity=(value.getProgress()+25)/100f;save();})
                    .setNegativeButton("Cancel",null).show();
            } else if (which == 1) {
                if (controls.size() >= TouchConfiguration.LIMIT) return;
                settings.overlayDisabled = false; saveFeatures();
                editing = true; menuTouch = false;
                add("custom"+System.nanoTime(),"NEW",BUTTON,PAD,.5f,.5f,.065f);
                save(); invalidate(); editControl(controls.get(controls.size()-1));
            } else if (which == 2) {
                new AlertDialog.Builder(activity).setMessage("Restore the default touchscreen layout and button actions?")
                    .setPositiveButton("Reset",(a,b)->{defaults(); for(Control c:controls)bound(c);save();invalidate();})
                    .setNegativeButton("Cancel",null).show();
            } else if (which == 3) new AlertDialog.Builder(activity).setTitle("How to play")
                .setMessage("MOVE: slide for analog movement. AIM: swipe to look. You can move, aim and hold fire together.\n\nMenus automatically use direct taps, including the profile keyboard. Tap letters and DONE to save your name. PAD shows controller buttons: arrows move, A selects, B cancels, X deletes and START finishes the name. TOUCH returns to tapping. In gameplay, MENU opens pause.\n\nEDIT: drag any control to move it. Tap a control to change its size, opacity and button action, or remove it. DONE saves the layout. OPTIONS lets you add buttons, reset the layout or change aim sensitivity.\n\nThe buttons are a gamepad, so they cannot type keyboard letters accidentally. Gameplay actions follow your controller profile.")
                .setPositiveButton("OK",null).show();
            else if (which == 4) generalSettings();
            else if (which == 5 || which == 6) ((HaloActivity)activity).chooseLayoutFile(which == 5, exportLayout());
            else if (which == 7) cheatSettings();
            else if (which == 8) {
                android.content.Intent intent = new android.content.Intent(activity, LauncherActivity.class);
                intent.putExtra("import-movies", true); activity.startActivity(intent);
            } else if (which == 9) nativeCameraMode();
            else if (which == 10) layoutPresets();
        }).show();
    }
    private void layoutPresets() {
        new AlertDialog.Builder(activity).setTitle("Layout presets")
            .setItems(new String[]{"OpenCE-Touch default", "fqlx compact"}, (dialog, selected) ->
                new AlertDialog.Builder(activity)
                    .setMessage("Replace the current button layout? Export it first to keep a copy. Your general settings stay the same.")
                    .setPositiveButton("Apply", (confirmation, button) -> {
                        releaseAll();
                        if (selected == 0) defaults();
                        else {
                            controls.clear();
                            for (TouchConfiguration.Button b : TouchConfiguration.compactLayout().buttons) {
                                Control c = new Control(b.id, b.label, b.kind, b.action, b.x, b.y, b.radius);
                                c.opacity = b.opacity; controls.add(c);
                            }
                        }
                        settings.overlayDisabled = false;
                        for (Control c : controls) bound(c);
                        save(); saveFeatures(); invalidate();
                    }).setNegativeButton("Cancel", null).show()).show();
    }
    // Mobile features adapted from theLlamaNet / FulGer. SDL virtual input stays in TouchInput.
    private final TouchConfiguration settings = new TouchConfiguration();
    private final GyroscopeAim gyroAim = new GyroscopeAim();
    private final float[] gyroDelta = new float[2];
    private android.hardware.SensorManager sensors;
    private android.hardware.Sensor gyroscope;
    private android.os.Vibrator vibrator;
    private boolean deviceInputActive, gyroRegistered, movieActive;
    private int currentFps, menuContext;
    private StartupCheats startupCheats;
    private static native int nativeRumble();
    private static native void nativeLookReset();
    private static native void nativeCameraMode();
    private static native boolean nativeCheatRequest(int id, boolean enabled);
    private static native int nativeCheatStatus(int id);
    private static native void nativeFieldOfView(float degrees);
    private static native int[] nativeMenuPoll();
    private static native void nativeMenuPublish(int revision, int page, boolean editing,
        String title, String[] labels, int[] actions, int[] values);

    private void loadFeatures() {
        settings.gyro = prefs.getBoolean("gyro", false); settings.rumble = prefs.getBoolean("rumble", true);
        settings.fps = prefs.getBoolean("fps", false); settings.icons = prefs.getBoolean("icons", true);
        settings.overlayDisabled = prefs.getBoolean("overlay-disabled", false);
        settings.gyroSensitivity = prefs.getFloat("gyro-sensitivity", 1f);
        if (!Float.isFinite(settings.gyroSensitivity) || settings.gyroSensitivity < .25f || settings.gyroSensitivity > 4f) settings.gyroSensitivity = 1f;
        settings.fov = prefs.getFloat("fov", 70f);
        if (!Float.isFinite(settings.fov) || settings.fov < 55f || settings.fov > 90f) settings.fov = 70f;
        nativeFieldOfView(settings.fov);
        sensors = (android.hardware.SensorManager)activity.getSystemService(android.content.Context.SENSOR_SERVICE);
        gyroscope = sensors == null ? null : sensors.getDefaultSensor(android.hardware.Sensor.TYPE_GYROSCOPE);
        vibrator = (android.os.Vibrator)activity.getSystemService(android.content.Context.VIBRATOR_SERVICE);
        java.io.File root = activity.getExternalFilesDir(null);
        if (root != null) try { startupCheats = new StartupCheats(new java.io.File(root,"init.txt").toPath()); }
        catch (java.io.IOException e) { toast("Cannot read startup cheats: " + e.getMessage()); }
        // Native Halo menus expose Porting options; Android dialogs provide the settings pages.
        nativeMenuPublish(1, 0, false, "Porting options", new String[0], new int[0], new int[0]);
    }
    private void saveFeatures() {
        prefs.edit().putBoolean("gyro", settings.gyro).putBoolean("rumble", settings.rumble)
            .putBoolean("fps",settings.fps).putBoolean("icons",settings.icons)
            .putBoolean("overlay-disabled",settings.overlayDisabled)
            .putFloat("gyro-sensitivity",settings.gyroSensitivity).putFloat("fov",settings.fov).apply();
        nativeFieldOfView(settings.fov); updateSensors(); invalidate();
    }
    private void toast(String s) { android.widget.Toast.makeText(activity,s,android.widget.Toast.LENGTH_LONG).show(); }
    public void startDeviceInput() { deviceInputActive = true; updateSensors(); }
    public void stopDeviceInput() {
        deviceInputActive = false; updateSensors();
        if (vibrator != null) try { vibrator.cancel(); } catch (RuntimeException ignored) {}
        releaseAll();
    }
    public void suspendForMovie(boolean suspended) {
        movieActive = suspended; releaseAll(); updateSensors();
        if (vibrator != null) try { vibrator.cancel(); } catch (RuntimeException ignored) {}
    }
    private void updateSensors() {
        boolean needed = deviceInputActive && !menus && !editing && !movieActive && !settings.overlayDisabled && settings.gyro && gyroscope != null;
        if (needed && !gyroRegistered) { gyroAim.reset(); gyroRegistered = sensors.registerListener(this,gyroscope,android.hardware.SensorManager.SENSOR_DELAY_GAME); }
        else if (!needed && gyroRegistered) { sensors.unregisterListener(this); gyroRegistered = false; gyroAim.reset(); }
    }
    @Override public void onAccuracyChanged(android.hardware.Sensor sensor, int accuracy) {}
    @Override public void onSensorChanged(android.hardware.SensorEvent event) {
        if (!deviceInputActive || !settings.gyro || menus || editing || movieActive || settings.overlayDisabled) { gyroAim.reset(); return; }
        int rotation = activity.getWindowManager().getDefaultDisplay().getRotation();
        if (gyroAim.sample(event.timestamp,event.values[0],event.values[1],rotation,gyroDelta))
            mouseMove(-gyroDelta[0]/.0022f*settings.gyroSensitivity,-gyroDelta[1]/.0022f*settings.gyroSensitivity,true);
    }
    private void pollFeatures() {
        updateSensors();
        if (!deviceInputActive || movieActive) return;
        int[] state = nativeMenuPoll();
        if (state != null) { currentFps = state[5]; menuContext = state[1]; if (state[2] == 1) options(); }
        if (vibrator != null && vibrator.hasVibrator()) try {
            int amplitude = settings.rumble && !menus && !editing && !settings.overlayDisabled ? nativeRumble() : 0;
            if (amplitude > 0) vibrator.vibrate(android.os.VibrationEffect.createOneShot(110,
                vibrator.hasAmplitudeControl() ? amplitude : android.os.VibrationEffect.DEFAULT_AMPLITUDE));
            else vibrator.cancel();
        } catch (RuntimeException ignored) {}
        if (settings.fps) invalidate();
    }
    private static int iconFor(int action) {
        if (action == CAMERA) return 18;
        int[] map = {0,1,2,3,11,-1,10,6,7,8,9,12,13,14,15,5,4};
        int i = action - PAD; return i >= 0 && i < map.length ? map[i] : -1;
    }
    private void generalSettings() {
        String[] rows = {"Gyroscope: " + (gyroscope == null ? "unavailable" : settings.gyro ? "ON" : "OFF"),
            "Gyroscope sensitivity", "Rumble: " + (vibrator == null || !vibrator.hasVibrator() ? "unavailable" : settings.rumble ? "ON" : "OFF"),
            "FPS counter: " + (settings.fps ? "ON" : "OFF"), "Field of view: " + Math.round(settings.fov),
            "Halo icons: " + (settings.icons ? "ON" : "OFF"), "Disable overlay: " + (settings.overlayDisabled ? "ON" : "OFF")};
        new AlertDialog.Builder(activity).setTitle("General settings").setItems(rows,(d,i)->{
            releaseAll();
            if (i == 0 && gyroscope != null) settings.gyro = !settings.gyro;
            else if (i == 1 || i == 4) {
                boolean fov = i == 4; LinearLayout layout = dialogLayout();
                SeekBar value = slider(layout,fov ? "Field of view (55–90 degrees)" : "Gyroscope sensitivity (0.25–4)",
                    fov ? 35 : 375, Math.round(fov ? settings.fov-55 : (settings.gyroSensitivity-.25f)*100));
                new AlertDialog.Builder(activity).setTitle(fov ? "Field of view" : "Gyroscope sensitivity").setView(layout)
                    .setPositiveButton("Save",(a,b)->{ if (fov) settings.fov=55+value.getProgress(); else settings.gyroSensitivity=.25f+value.getProgress()/100f; saveFeatures(); })
                    .setNegativeButton("Cancel",null).show();return;
            } else if (i == 2) settings.rumble = !settings.rumble;
            else if (i == 3) settings.fps = !settings.fps;
            else if (i == 5) settings.icons = !settings.icons;
            else if (i == 6) settings.overlayDisabled = !settings.overlayDisabled;
            saveFeatures(); generalSettings();
        }).setNegativeButton("Close",null).show();
    }
    private static final String[] CHEATS = {"Invincibility","Jetpack","Infinite ammo","Bump possession","Super jump","Reflexive damage","Medusa","Omnipotent","Controller cheats","Bottomless clip","Active camouflage (player)","Active camouflage","All powerups","All vehicles","All weapons","Teleport to camera"};
    private void cheatSettings() {
        String[] rows = CHEATS.clone();
        boolean startup = menuContext == 1;
        for (int i=0;i<rows.length;i++) if (i<10 || startup) rows[i] += startup ? startupCheats != null && startupCheats.enabled(i) ? ": ON" : ": OFF" : nativeCheatStatus(i)==1 ? ": ON" : ": OFF";
        new AlertDialog.Builder(activity).setTitle(startup ? "Startup cheats (single-player)" : "Single-player cheats").setItems(rows,(d,i)->{
            if (startup) { if (startupCheats != null) try { startupCheats.toggle(i); } catch (java.io.IOException e) { toast("Cannot save cheats: "+e.getMessage()); } }
            else if (!nativeCheatRequest(i,i>=10 || nativeCheatStatus(i)!=1)) toast("Cheat request is busy");
            cheatSettings();
        }).setNegativeButton("Close",null).show();
    }
    public String exportLayout() {
        TouchConfiguration c = settings; c.buttons.clear(); c.sensitivity = sensitivity;
        for (Control control: controls) {
            TouchConfiguration.Button b=new TouchConfiguration.Button(); b.id=control.id;b.label=control.label;b.kind=control.kind;b.action=control.action;
            b.x=control.x;b.y=control.y;b.radius=control.radius;b.opacity=control.opacity;c.buttons.add(b);
        }
        return c.encode();
    }
    public void importLayout(String text) {
        TouchConfiguration c=TouchConfiguration.decode(text); ArrayList<Control> next=new ArrayList<>();
        for (TouchConfiguration.Button b:c.buttons) { Control control=new Control(b.id,b.label,b.kind,b.action,b.x,b.y,b.radius);control.opacity=b.opacity;next.add(control); }
        releaseAll(); controls.clear(); controls.addAll(next); sensitivity=c.sensitivity;
        settings.gyro=c.gyro;settings.gyroSensitivity=c.gyroSensitivity;settings.rumble=c.rumble;settings.fps=c.fps;settings.fov=c.fov;
        settings.icons=c.icons;settings.overlayDisabled=c.overlayDisabled;
        for(Control control:controls)bound(control); save();saveFeatures();
    }
}
