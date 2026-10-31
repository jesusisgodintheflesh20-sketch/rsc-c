package org.scape2003.mudclient;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.widget.LinearLayout;
import android.widget.SeekBar;
import android.widget.TextView;
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

    private static SharedPreferences preferences(Context context) {
        return context.getSharedPreferences("offline_audio", Context.MODE_PRIVATE);
    }

    private static void addVolumeSlider(Activity activity, LinearLayout layout,
                                        String label, String key, int defaultVolume) {
        SharedPreferences prefs = preferences(activity);
        TextView title = new TextView(activity);
        SeekBar slider = new SeekBar(activity);
        slider.setMax(100);
        slider.setProgress(prefs.getInt(key, defaultVolume));
        title.setText(label + ": " + slider.getProgress() + "%");
        layout.addView(title);
        layout.addView(slider);
        slider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            public void onProgressChanged(SeekBar bar, int value, boolean fromUser) {
                title.setText(label + ": " + value + "%");
                if (!fromUser) return;
                prefs.edit().putInt(key, value).apply();
                MediaPlayer player = key.equals("music") ? music : forest;
                if (player != null) player.setVolume(value / 100f, value / 100f);
            }
            public void onStartTrackingTouch(SeekBar bar) {}
            public void onStopTrackingTouch(SeekBar bar) {}
        });
    }

    public static void showVolumeSettings(Activity activity) {
        LinearLayout layout = new LinearLayout(activity);
        layout.setOrientation(LinearLayout.VERTICAL);
        int padding = (int) (24 * activity.getResources().getDisplayMetrics().density);
        layout.setPadding(padding, padding / 2, padding, 0);
        addVolumeSlider(activity, layout, "Music", "music", 32);
        addVolumeSlider(activity, layout, "Ambient sound", "forest", 25);
        new AlertDialog.Builder(activity).setTitle("Sound")
            .setView(layout).setPositiveButton("Done", null).show();
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
        if (forest == null) forest = createPlayer(context, "forest-ambient.m4a", preferences(context).getInt("forest", 25) / 100f);
        if (music == null) music = createPlayer(context, "background-music.m4a", preferences(context).getInt("music", 32) / 100f);
        start(forest, "Forest ambience playing");
        start(music, "Background music playing");
    }
}
