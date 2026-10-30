#include <jni.h>
#include <stdlib.h>
#include <unistd.h>
int sundae_main(int argc, char **argv);
JNIEXPORT jint JNICALL Java_org_scape2003_mudclient_OfflineService_runWorld(JNIEnv *env, jclass cls, jstring directory) {
    (void)cls;
    const char *dir = (*env)->GetStringUTFChars(env, directory, NULL);
    char *argv[] = {"sundae", "-b", (char *)dir, "-f", "settings.ini", NULL};
    /* This is a separate process, so changing cwd cannot affect the client. */
    if (chdir(dir) != 0) return -1;
    int result = sundae_main(5, argv);
    (*env)->ReleaseStringUTFChars(env, directory, dir);
    return result;
}
