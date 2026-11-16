from media.player import Player, K_PLAYER_EVENT_EOF
import os
import time
import sys

class MP4Player:
    def __init__(self, filepath):
        self.filepath = filepath
        self._is_playing = False
        self.player = Player()

    def _event_callback(self, event, data):
        """播放器事件回调函数"""
        if event == K_PLAYER_EVENT_EOF:
            self._is_playing = False

    def play(self):
        """启动播放流程"""
        try:
            self.player.load(self.filepath)
            self.player.set_event_callback(self._event_callback)
            self.player.start()
            self._is_playing = True

            print(f"Start playing: {self.filepath}")
            while self._is_playing:
                time.sleep(0.1)
                os.exitpoint()

        except KeyboardInterrupt:
            print("User interrupted playback.")
        except Exception as e:
            sys.print_exception(e)
        finally:
            self.stop()

    def stop(self):
        """停止播放并清理资源"""
        if self.player:
            self.player.stop()
        print("Playback finished.")

def main():
    os.exitpoint(os.EXITPOINT_ENABLE)
    video_path = "/sdcard/examples/test.mp4"
    player = MP4Player(video_path)
    player.play()

if __name__ == "__main__":
    main()
