package org.scape2003.mudclient;

import org.libsdl.app.SDLActivity;

public class mudclientActivity extends SDLActivity {
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
