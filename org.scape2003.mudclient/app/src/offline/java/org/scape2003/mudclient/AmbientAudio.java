package org.scape2003.mudclient;

import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.util.Log;
import java.io.IOException;

/** All methods are called on the activity's UI thread. */
public final class AmbientAudio {
    private static MediaPlayer player;
    private static boolean enabled;
    private static boolean resumed;
    private AmbientAudio() {}

    public static void setState(Context context, int state) {
        if (state == -4) {
            enabled = false;
            if (player != null) { player.release(); player = null; }
            return;
        }
        if (state == -2) resumed = false;
        else if (state == -3) resumed = true;
        else enabled = state == 1;
        if (!enabled || !resumed) {
            if (player != null && player.isPlaying()) player.pause();
            return;
        }
        if (player == null) {
            try (AssetFileDescriptor file = context.getAssets().openFd("forest-ambient.m4a")) {
                MediaPlayer next = new MediaPlayer();
                try {
                    next.setAudioStreamType(AudioManager.STREAM_MUSIC);
                    next.setDataSource(file.getFileDescriptor(), file.getStartOffset(), file.getLength());
                    next.setLooping(true);
                    next.setVolume(0.25f, 0.25f);
                    next.prepare();
                    player = next;
                } catch (IOException | RuntimeException error) {
                    next.release();
                    throw error;
                }
            } catch (IOException | RuntimeException error) {
                Log.e("AmbientAudio", "Unable to load forest audio", error);
                return;
            }
        }
        if (!player.isPlaying()) {
            player.start();
            Log.i("AmbientAudio", "Forest ambience playing");
        }
    }
}
