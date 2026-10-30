package org.scape2003.mudclient;

import org.libsdl.app.SDLActivity;

public class mudclientActivity extends SDLActivity
{
    // Invoked from SDL's native thread only by the offline build.
    public boolean startOfflineWorld() {
        try {
            return (Boolean) Class.forName("org.scape2003.mudclient.OfflineWorld")
                .getMethod("start", android.content.Context.class).invoke(null, this);
        } catch (Exception error) {
            android.util.Log.e("OfflineWorld", "Cannot start local world", error);
            return false;
        }
    }
}
