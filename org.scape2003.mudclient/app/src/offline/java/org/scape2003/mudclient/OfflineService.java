package org.scape2003.mudclient;

import android.app.Service;
import android.content.Intent;
import android.os.IBinder;
import java.io.File;

/** Server globals and cwd are isolated from SDL in the :offline process. */
public final class OfflineService extends Service {
    private boolean started;
    private static native int runWorld(String directory);
    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        if (!started) {
            started = true;
            new Thread(() -> {
                try {
                    System.loadLibrary("sundae");
                    int result = runWorld(new File(getFilesDir(), "world-2001").getAbsolutePath());
                    android.util.Log.e("OfflineWorld", "Server exited: " + result);
                } catch (Throwable error) { android.util.Log.e("OfflineWorld", "Server failed", error); }
                stopSelf();
            }, "offline-world").start();
        }
        return START_NOT_STICKY;
    }
    @Override public IBinder onBind(Intent intent) { return null; }
    @Override public void onDestroy() {
        super.onDestroy();
        // A stopped world must release its socket and native state before the next launch.
        android.os.Process.killProcess(android.os.Process.myPid());
    }
}
