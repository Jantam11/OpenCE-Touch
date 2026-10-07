package com.halo.decomp;

import java.io.StringReader;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.Properties;

/** Portable layouts inspired by theLlamaNet's TouchLayout; preserves our actions and opacity. */
final class TouchConfiguration {
    static final int LIMIT = 65;
    static final class Button {
        String id, label;
        int kind, action;
        float x, y, radius, opacity;
    }
    final ArrayList<Button> buttons = new ArrayList<>();
    float sensitivity = 1.8f, gyroSensitivity = 1f, fov = 70f;
    boolean gyro, rumble = true, fps, icons = true, overlayDisabled;

    private static float number(Properties p, String key, float fallback, float low, float high) {
        float n = Float.parseFloat(p.getProperty(key, Float.toString(fallback)));
        if (!Float.isFinite(n) || n < low || n > high) throw new IllegalArgumentException("Invalid " + key);
        return n;
    }
    private static boolean bool(Properties p, String key, boolean fallback) {
        String s = p.getProperty(key, Boolean.toString(fallback));
        if (!s.equals("true") && !s.equals("false")) throw new IllegalArgumentException("Invalid " + key);
        return Boolean.parseBoolean(s);
    }
    static boolean validAction(int action) { return action == 0 || action == 2000 || action >= 1000 && action <= 1016; }

    String encode() {
        Properties p = new Properties();
        p.setProperty("format", "opence-touch-layout"); p.setProperty("version", "1");
        p.setProperty("count", Integer.toString(buttons.size()));
        p.setProperty("sensitivity", Float.toString(sensitivity));
        p.setProperty("gyroscope-sensitivity", Float.toString(gyroSensitivity));
        p.setProperty("field-of-view", Float.toString(fov));
        p.setProperty("gyroscope", Boolean.toString(gyro)); p.setProperty("rumble", Boolean.toString(rumble));
        p.setProperty("fps-counter", Boolean.toString(fps)); p.setProperty("icons", Boolean.toString(icons));
        p.setProperty("overlay-disabled", Boolean.toString(overlayDisabled));
        for (int i = 0; i < buttons.size(); i++) {
            Button b = buttons.get(i); String k = "control." + i + ".";
            p.setProperty(k+"id", b.id); p.setProperty(k+"label", b.label);
            p.setProperty(k+"kind", Integer.toString(b.kind)); p.setProperty(k+"action", Integer.toString(b.action));
            p.setProperty(k+"x", Float.toString(b.x)); p.setProperty(k+"y", Float.toString(b.y));
            p.setProperty(k+"radius", Float.toString(b.radius)); p.setProperty(k+"opacity", Float.toString(b.opacity));
        }
        try { StringWriter s = new StringWriter(); p.store(s, "OpenCE-Touch layout"); return s.toString(); }
        catch (java.io.IOException e) { throw new IllegalStateException(e); }
    }

    static TouchConfiguration decode(String text) {
        if (text == null || text.length() > 65536) throw new IllegalArgumentException("Layout file is too large");
        Properties p = new Properties();
        try { p.load(new StringReader(text)); } catch (java.io.IOException e) { throw new IllegalArgumentException(e); }
        boolean llama = "halo-touch-layout".equals(p.getProperty("format"));
        String version = p.getProperty("version", "");
        if (!(llama && version.matches("[1-4]") || "opence-touch-layout".equals(p.getProperty("format")) && version.equals("1")))
            throw new IllegalArgumentException("Unsupported layout format");
        int count = Integer.parseInt(p.getProperty("count", "0"));
        if (count < 1 || count > LIMIT) throw new IllegalArgumentException("Invalid number of controls");
        TouchConfiguration c = new TouchConfiguration();
        c.sensitivity = number(p,"sensitivity",1.8f,.25f,5f);
        c.gyroSensitivity = number(p,"gyroscope-sensitivity",1f,.25f,4f);
        c.fov = number(p,"field-of-view",70f,55f,90f);
        c.gyro = bool(p,"gyroscope",false); c.rumble = bool(p,"rumble",true);
        c.fps = bool(p,"fps-counter",false); c.icons = bool(p,"icons",true);
        c.overlayDisabled = bool(p,"overlay-disabled",false);
        int[] actions = {1000,1001,1002,1003,1016,1015,1007,1008,1009,1010,1006,1004,1011,1012,1013,1014,0,1016,2000};
        String[] labels = {"A","B","X","Y","FIRE","GRENADE","CROUCH","ZOOM","LIGHT","GREN TYPE","PAUSE","SCORE","UP","DOWN","LEFT","RIGHT","MOVE","FIRE","CAMERA"};
        java.util.HashSet<String> ids = new java.util.HashSet<>();
        int movement = 0;
        for (int i = 0; i < count; i++) {
            String k = "control."+i+"."; Button b = new Button();
            if (llama) {
                int type = Integer.parseInt(p.getProperty(k+"type", "-1"));
                if (type < 0 || type >= (version.equals("4") ? 19 : 18)) throw new IllegalArgumentException("Invalid control type");
                if (!bool(p,k+"visible",true)) continue;
                b.id = "imported"+i; b.label = labels[type]; b.kind = type == 16 ? 1 : 0; b.action = actions[type];
                b.x = number(p,k+"x",480f,0f,960f)/960f; b.y = number(p,k+"y",270f,0f,540f)/540f;
                b.radius = (type == 16 ? .12f : .065f)*number(p,k+"size",1f,.5f,2f); b.opacity = .45f;
            } else {
                b.id = p.getProperty(k+"id", ""); b.label = p.getProperty(k+"label", "");
                b.kind = Integer.parseInt(p.getProperty(k+"kind", "-1"));
                b.action = Integer.parseInt(p.getProperty(k+"action", "-1"));
                b.x = number(p,k+"x",.5f,0f,1f); b.y = number(p,k+"y",.5f,0f,1f);
                b.radius = number(p,k+"radius",.065f,.025f,.3f); b.opacity = number(p,k+"opacity",.45f,.1f,.9f);
            }
            if (b.kind < 0 || b.kind > 2 || !validAction(b.action) || b.id.isEmpty() || b.id.length() > 96 ||
                    b.label.length() > 96 || !ids.add(b.id) || b.kind == 1 && ++movement > 1)
                throw new IllegalArgumentException("Invalid control in layout");
            c.buttons.add(b);
        }
        if (c.buttons.isEmpty()) throw new IllegalArgumentException("Layout hides every control");
        // Foreign layouts aim on empty screen space. Our virtual pad uses an
        // explicit aim region, so include one when translating those layouts.
        if (llama) {
            if (c.buttons.size() == LIMIT) throw new IllegalArgumentException("Layout needs room for an aim pad");
            Button aim = new Button();
            aim.id = "importedAim"; aim.label = "AIM"; aim.kind = 2;
            aim.x = .72f; aim.y = .52f; aim.radius = .16f; aim.opacity = .3f;
            c.buttons.add(aim);
        }
        return c;
    }
}
