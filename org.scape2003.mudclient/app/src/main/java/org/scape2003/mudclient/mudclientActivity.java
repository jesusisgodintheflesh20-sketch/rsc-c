package org.scape2003.mudclient;

import org.libsdl.app.SDLActivity;

public class mudclientActivity extends SDLActivity {
    public void setOfflineAmbient(int state) {
        runOnUiThread(() -> {
            try {
                Class<?> audio = Class.forName("org.scape2003.mudclient.AmbientAudio");
                if (state == -5) {
                    audio.getMethod("showVolumeSettings", android.app.Activity.class)
                        .invoke(null, this);
                } else {
                    audio.getMethod("setState", android.content.Context.class, int.class)
                        .invoke(null, this, state);
                }
            } catch (ClassNotFoundException ignored) {
                // Online builds do not bundle ambient audio.
            } catch (Exception error) {
                android.util.Log.e("AmbientAudio", "Unable to update ambience", error);
            }
        });
    }
    @Override protected void onPause() { setOfflineAmbient(-2); super.onPause(); }
    @Override protected void onResume() { super.onResume(); setOfflineAmbient(-3); }
    @Override protected void onDestroy() { setOfflineAmbient(-4); super.onDestroy(); }

    // Reflection keeps the online build independent of the offline-only classes.
    public boolean startOfflineWorld() {
        try {
            Class.forName("org.scape2003.mudclient.OfflineWorld")
                .getMethod("begin", android.content.Context.class).invoke(null, this);
            return true;
        } catch (Exception error) {
            android.util.Log.e("OfflineWorld", "Cannot start local world", error);
            return false;
        }
    }

    public String offlineWorldFailure() {
        try {
            return (String) Class.forName("org.scape2003.mudclient.OfflineWorld")
                .getMethod("getFailure").invoke(null);
        } catch (Exception error) { return "Could not read engine status"; }
    }

    public int offlineWorldState() {
        try {
            return (Integer) Class.forName("org.scape2003.mudclient.OfflineWorld")
                .getMethod("getState").invoke(null);
        } catch (Exception error) {
            android.util.Log.e("OfflineWorld", "Cannot check local world", error);
            return -1;
        }
    }
}
