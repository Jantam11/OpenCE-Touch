package com.halo.decomp;

import android.content.Context;
import android.graphics.Insets;
import android.os.Build;
import android.view.View;
import android.view.WindowInsets;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.view.Display;
import android.view.WindowManager;

import org.libsdl.app.SDLActivity;

/**
 * The game: SDL3's activity, running libmain.so (port/android/host), which
 * loads the game image from the APK's assets.
 */
public class HaloActivity extends SDLActivity {
    /** lets system link's broadcasts in over Wi-Fi while the game runs */
    private WifiManager.MulticastLock multicastLock;
    private TouchControls touchControls;
    private MoviePlayer moviePlayer;
    private volatile int[] gestureInsets = new int[] {0, 0, 0, 0};

    @Override
    protected String[] getLibraries() {
        return new String[] { "SDL3", "main" };
    }

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (savedInstanceState != null) pendingLayoutExport = savedInstanceState.getString("pending-layout-export");
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        preferHighestRefreshRate();
        trackGestureInsets();
        acquireMulticastLock();
        touchControls = new TouchControls(this);
        addContentView(touchControls, new android.view.ViewGroup.LayoutParams(
                android.view.ViewGroup.LayoutParams.MATCH_PARENT,
                android.view.ViewGroup.LayoutParams.MATCH_PARENT));
        if (mLayout != null) moviePlayer = new MoviePlayer(this,mLayout,touchControls);
        // a new version looked for while the game starts
        Updater.start(this);
    }

    @Override
    protected void onDestroy() {
        if (moviePlayer != null) moviePlayer.close();
        if (touchControls != null) touchControls.stopDeviceInput();
        if (multicastLock != null && multicastLock.isHeld())
            multicastLock.release();
        multicastLock = null;
        super.onDestroy();
    }

    @Override
    protected void onPause() {
        if (moviePlayer != null) moviePlayer.pause();
        if (touchControls != null) touchControls.stopDeviceInput();
        super.onPause();
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        if (touchControls != null) { if (hasFocus) touchControls.startDeviceInput(); else touchControls.stopDeviceInput(); }
        super.onWindowFocusChanged(hasFocus);
    }

    /**
     * keeps gestureInsets current; Android sends the insets again when the
     * activity rotates (after the game's native code has started on a phone
     * launched from portrait), so a single read at startup would keep the
     * portrait values; the listener hands the insets on so SDL's own
     * handling still sees them
     */
    private void trackGestureInsets() {
        getWindow().getDecorView().setOnApplyWindowInsetsListener(new View.OnApplyWindowInsetsListener() {
            @Override
            public WindowInsets onApplyWindowInsets(View view, WindowInsets insets) {
                gestureInsets = readGestureInsets(insets);
                return view.onApplyWindowInsets(insets);
            }
        });
    }

    @SuppressWarnings("deprecation") // getSystemGestureInsets is the only call on Android 10
    private static int[] readGestureInsets(WindowInsets insets) {
        Insets gesture;

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R)
            gesture = insets.getInsets(WindowInsets.Type.systemGestures());
        else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q)
            gesture = insets.getSystemGestureInsets();
        else
            return new int[] { 0, 0, 0, 0 };
        return new int[] { gesture.left, gesture.top, gesture.right, gesture.bottom };
    }

    /**
     * the edges of the screen where Android keeps its gestures; in sticky
     * full screen the first swipe from an edge only shows the system bars,
     * and Android hands that swipe to the game as an ordinary finger, so
     * the game (port/linux/src/touch_input.c) must ignore touches that
     * begin there; returns a copy of {left, top, right, bottom} in pixels:
     * all 0 before Android 10 (which has no insets) and until the first
     * insets arrive. The game's native code calls this through JNI by name
     * and signature (host_main.c GetMethodID(...,
     * "getSystemGestureInsetsPixels", "()[I")), at every finger down, so
     * it must not be renamed, retyped or removed as unused
     */
    public int[] getSystemGestureInsetsPixels() {
        return gestureInsets.clone();
    }

    /**
     * Many phones drop the Wi-Fi's broadcast and multicast datagrams to
     * save power unless an app holds this: without it they would not see
     * system link games on the local network, nor be seen hosting one.
     */
    private void acquireMulticastLock() {
        try {
            WifiManager wifi = (WifiManager) getApplicationContext().getSystemService(Context.WIFI_SERVICE);
            if (wifi == null)
                return;
            multicastLock = wifi.createMulticastLock("halo-system-link");
            multicastLock.setReferenceCounted(false);
            multicastLock.acquire();
        } catch (RuntimeException e) {
            // (no Wi-Fi, or not allowed: the local network may miss games)
            multicastLock = null;
        }
    }

    /**
     * The game draws a frame at every display refresh, between its 30 Hz
     * ticks (port/linux/game/render_interpolation.c); Android otherwise
     * often keeps an app at 60 Hz on a faster display.
     */
    private void preferHighestRefreshRate() {
        Display display = getWindowManager().getDefaultDisplay();
        Display.Mode current = display.getMode();
        Display.Mode best = current;

        for (Display.Mode mode : display.getSupportedModes()) {
            if (mode.getPhysicalWidth() == current.getPhysicalWidth() &&
                mode.getPhysicalHeight() == current.getPhysicalHeight() &&
                mode.getRefreshRate() > best.getRefreshRate()) {
                best = mode;
            }
        }
        WindowManager.LayoutParams attributes = getWindow().getAttributes();
        attributes.preferredDisplayModeId = best.getModeId();
        getWindow().setAttributes(attributes);
    }
    private static final int EXPORT_LAYOUT = 401, IMPORT_LAYOUT = 402;
    private String pendingLayoutExport;
    public void chooseLayoutFile(boolean export, String contents) {
        pendingLayoutExport = export ? contents : null;
        android.content.Intent intent = new android.content.Intent(export ? android.content.Intent.ACTION_CREATE_DOCUMENT : android.content.Intent.ACTION_OPEN_DOCUMENT);
        intent.addCategory(android.content.Intent.CATEGORY_OPENABLE); intent.setType(export ? "text/plain" : "*/*");
        if (export) intent.putExtra(android.content.Intent.EXTRA_TITLE,"opence-touch.halolayout");
        try { startActivityForResult(intent,export ? EXPORT_LAYOUT : IMPORT_LAYOUT); }
        catch (android.content.ActivityNotFoundException e) { pendingLayoutExport = null; layoutError("No document picker is available"); }
    }
    @Override protected void onSaveInstanceState(android.os.Bundle state) {
        state.putString("pending-layout-export",pendingLayoutExport); super.onSaveInstanceState(state);
    }
    @Override protected void onActivityResult(int request, int result, android.content.Intent data) {
        if (request != EXPORT_LAYOUT && request != IMPORT_LAYOUT) { super.onActivityResult(request,result,data); return; }
        String export = pendingLayoutExport; pendingLayoutExport = null;
        if (result != RESULT_OK || data == null || data.getData() == null) return;
        android.net.Uri uri = data.getData();
        new Thread(()->{
            try {
                if (request == EXPORT_LAYOUT) {
                    if (export == null) throw new java.io.IOException("Layout snapshot is unavailable");
                    try (java.io.OutputStream out = getContentResolver().openOutputStream(uri,"wt")) {
                        if (out == null) throw new java.io.IOException("Cannot open destination");
                        out.write(export.getBytes(java.nio.charset.StandardCharsets.UTF_8));
                    }
                    runOnUiThread(()->android.widget.Toast.makeText(this,"Layout exported",android.widget.Toast.LENGTH_SHORT).show());
                } else {
                    java.io.ByteArrayOutputStream bytes = new java.io.ByteArrayOutputStream();
                    try (java.io.InputStream in=getContentResolver().openInputStream(uri)) {
                        if (in==null) throw new java.io.IOException("Cannot open file");
                        byte[] buffer=new byte[4096];int n;
                        while ((n=in.read(buffer))!=-1) { if (bytes.size()+n>65536) throw new java.io.IOException("Layout file is too large");bytes.write(buffer,0,n); }
                    }
                    String text=new String(bytes.toByteArray(),java.nio.charset.StandardCharsets.UTF_8); TouchConfiguration.decode(text);
                    runOnUiThread(()->{if(isFinishing()||isDestroyed())return;try{touchControls.importLayout(text);}catch(IllegalArgumentException e){layoutError(e.getMessage());}});
                }
            } catch (Exception e) { runOnUiThread(()->layoutError(e.getMessage())); }
        },"opence-layout-file").start();
    }
    private void layoutError(String message) {
        if(!isFinishing()&&!isDestroyed())new android.app.AlertDialog.Builder(this).setTitle("Layout file").setMessage(message).setPositiveButton("OK",null).show();
    }
    @Override protected void onResume() {
        super.onResume();
        if(touchControls!=null)touchControls.startDeviceInput();
        if(moviePlayer!=null)moviePlayer.resume();
    }
}
