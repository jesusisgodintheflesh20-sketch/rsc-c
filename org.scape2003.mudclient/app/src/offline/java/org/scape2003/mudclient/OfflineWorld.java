package org.scape2003.mudclient;

import android.content.Context;
import android.content.Intent;
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
    public static synchronized boolean start(Context context) {
        try {
            File directory = new File(context.getFilesDir(), "world-2001");
            // Refresh only immutable assets. SQLite saves live beside them and are never overwritten.
            File marker = new File(directory, ".assets-v1");
            if (!marker.exists()) {
                unpack(context, "offline-world", directory);
                if (!marker.createNewFile()) throw new IOException("Cannot mark extracted assets");
            }
            context.startService(new Intent(context, OfflineService.class));
            for (int i = 0; i < 300; i++) {
                try (Socket socket = new Socket()) {
                    socket.connect(new InetSocketAddress("127.0.0.1", 43595), 100);
                    return true;
                } catch (IOException notReady) { Thread.sleep(100); }
            }
        } catch (Exception error) { android.util.Log.e("OfflineWorld", "World startup failed", error); }
        return false;
    }
}
