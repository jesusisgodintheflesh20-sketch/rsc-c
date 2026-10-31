package org.scape2003.mudclient;

import android.content.Context;
import android.content.Intent;
import android.os.SystemClock;
import java.io.*;
import java.net.*;

public final class OfflineWorld {
    private static void unpack(Context context, String asset, File target) throws IOException {
        String[] children = context.getAssets().list(asset);
        if (children != null && children.length > 0) {
            if (!target.isDirectory() && !target.mkdirs()) throw new IOException("Cannot create " + target);
            for (String child : children) unpack(context, asset + "/" + child, new File(target, child));
        } else {
            try (InputStream in = context.getAssets().open(asset); OutputStream out = new FileOutputStream(target)) {
                byte[] buffer = new byte[16384];
                int count;
                while ((count = in.read(buffer)) != -1) out.write(buffer, 0, count);
            }
        }
    }
    private static final Object unpackLock = new Object();
    private static final long START_TIMEOUT_MS = 45000;
    // 0 idle, 1 starting, 2 ready, -1 failed.
    private static int state;
    private static Context appContext;
    private static long startedAt;
    private static int generation;

    public static synchronized void begin(Context context) {
        if (state == 1) return;
        state = 1;
        startedAt = SystemClock.elapsedRealtime();
        final int attempt = ++generation;
        final Context app = context.getApplicationContext();
        appContext = app;
        new Thread(() -> launch(app, attempt), "offline-startup").start();
    }

    public static synchronized int getState() {
        if (state == 1 && SystemClock.elapsedRealtime() - startedAt > START_TIMEOUT_MS) {
            state = -1;
            ++generation;
            android.util.Log.e("OfflineWorld", "Local world start timed out");
        }
        return state;
    }

    public static synchronized String getFailure() {
        if (appContext == null) return "Startup failed";
        File file = new File(appContext.getFilesDir(), "world-2001/startup-status.txt");
        try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
            String line = reader.readLine();
            return line == null ? "No engine status" : line;
        } catch (IOException error) { return "Could not start world service"; }
    }

    private static synchronized boolean isCurrent(int attempt) {
        return state == 1 && generation == attempt;
    }

    private static synchronized void finish(int attempt, int result) {
        if (generation == attempt && state == 1) state = result;
    }

    private static void launch(Context context, int attempt) {
        try {
            File directory = new File(context.getFilesDir(), "world-2001");
            // Only bundled assets are replaced; the SQLite database and WAL stay intact.
            synchronized (unpackLock) {
                if (!isCurrent(attempt)) return;
                File marker = new File(directory, ".assets-v2");
                if (!marker.exists()) {
                    unpack(context, "offline-world", directory);
                    if (!marker.createNewFile()) throw new IOException("Cannot mark extracted assets");
                }
            }
            if (!isCurrent(attempt)) return;
            context.startService(new Intent(context, OfflineService.class));
            while (isCurrent(attempt)) {
                if (getState() != 1) return;
                try (Socket socket = new Socket()) {
                    socket.connect(new InetSocketAddress("127.0.0.1", 43595), 100);
                    finish(attempt, 2);
                    return;
                } catch (IOException notReady) { Thread.sleep(100); }
            }
        } catch (Exception error) {
            android.util.Log.e("OfflineWorld", "World startup failed", error);
            finish(attempt, -1);
        }
    }
}
