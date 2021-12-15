#!/usr/bin/env python
import sys
import signal
import gi
gi.require_version('Gst', '1.0')
#gi.require_version('Gtk', '4.0')
from gi.repository import GObject, Gst, GLib #, Gtk

# print('Press Ctrl+C')
# signal.pause()

# gst-launch-1.0 pulsesrc ! audioconvert ! vorbisenc ! oggmux ! filesink location=dump.ogg
# gst-launch-1.0 playbin uri=file:///path/to/dump.ogg

def bus_call(bus, message, loop):
    sys.stdout.write(f"bus_call {message.type}\n")
    t = message.type
    if t == Gst.MessageType.EOS:
        sys.stdout.write("End-of-stream\n")
        loop.quit()
    elif t == Gst.MessageType.ERROR:
        err, debug = message.parse_error()
        sys.stderr.write("Error: %s: %s\n" % (err, debug))
        loop.quit()
    return True

def main(args):
    if len(args) != 2:
        sys.stderr.write("usage: %s <output file>\n" % args[0])
        sys.exit(1)

    output_file_url = args[1]

    # GObject.threads_init()
    Gst.init(None)

    pipeline = Gst.Pipeline()

    pulsesrc = Gst.ElementFactory.make("alsasrc", "alsasrc")
    audioconvert = Gst.ElementFactory.make("audioconvert", "audioconvert")
    vorbisenc = Gst.ElementFactory.make("vorbisenc", "vorbisenc")
    oggmux = Gst.ElementFactory.make("oggmux", "oggmux")
    filesink = Gst.ElementFactory.make("filesink", "filesink")
    filesink.set_property("location", output_file_url)

    pipeline.add(pulsesrc)
    pipeline.add(audioconvert)
    pipeline.add(vorbisenc)
    pipeline.add(oggmux)
    pipeline.add(filesink)

    pulsesrc.link(audioconvert)
    audioconvert.link(vorbisenc)
    vorbisenc.link(oggmux)
    oggmux.link(filesink)

    loop = GLib.MainLoop()

    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect ("message", bus_call, loop)

    pipeline.set_state(Gst.State.PLAYING)


    def sigint_handler(sig, frame):
        pipeline.send_event(Gst.Event.new_eos())

    signal.signal(signal.SIGINT, sigint_handler)

    try:
      loop.run()
    except:
      pass

    sys.stdout.write(f"loop terminated\n")


    # cleanup
    # playbin.set_state(Gst.State.NULL)
    pipeline.set_state(Gst.State.NULL)

    sys.stdout.write(f"piepline set to null\n")

    # gst_object_unref (sink);
    # gst_object_unref (pipeline);

    # Gtk.main()

if __name__ == "__main__":
    sys.exit(main(sys.argv))


