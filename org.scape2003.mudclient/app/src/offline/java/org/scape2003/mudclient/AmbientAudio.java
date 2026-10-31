package org.scape2003.mudclient;

import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.util.Log;
import java.io.IOException;

/** All methods are called on the activity's UI thread. */
public final class AmbientAudio {
    private static MediaPlayer forest;
    private static MediaPlayer music;
    private static boolean enabled;
    private static boolean resumed;
    private AmbientAudio() {}

    private static MediaPlayer createPlayer(Context context, String asset, float volume) {
        try (AssetFileDescriptor file = context.getAssets().openFd(asset)) {
            MediaPlayer next = new MediaPlayer();
            try {
                next.setAudioStreamType(AudioManager.STREAM_MUSIC);
                next.setDataSource(file.getFileDescriptor(), file.getStartOffset(), file.getLength());
                next.setLooping(true);
                next.setVolume(volume, volume);
                next.prepare();
                return next;
            } catch (IOException | RuntimeException error) {
                next.release();
                throw error;
            }
        } catch (IOException | RuntimeException error) {
            Log.e("AmbientAudio", "Unable to load " + asset, error);
            return null;
        }
    }

    private static void pause(MediaPlayer player) {
        if (player != null && player.isPlaying()) player.pause();
    }

    private static void start(MediaPlayer player, String message) {
        if (player != null && !player.isPlaying()) {
            player.start();
            Log.i("AmbientAudio", message);
        }
    }

    public static void setState(Context context, int state) {
        if (state == -4) {
            enabled = false;
            if (forest != null) { forest.release(); forest = null; }
            if (music != null) { music.release(); music = null; }
            return;
        }
        if (state == -2) resumed = false;
        else if (state == -3) resumed = true;
        else enabled = state == 1;
        if (!enabled || !resumed) {
            pause(forest);
            pause(music);
            return;
        }
        if (forest == null) forest = createPlayer(context, "forest-ambient.m4a", 0.25f);
        if (music == null) music = createPlayer(context, "background-music.m4a", 0.32f);
        start(forest, "Forest ambience playing");
        start(music, "Background music playing");
    }
}
