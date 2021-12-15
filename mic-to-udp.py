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

# server
# gst-launch-1.0 filesrc location=path/to/file.mp3 ! mpegaudioparse ! mpg123audiodec ! audioconvert ! rtpL24pay ! udpsink host=127.0.0.1 auto-multicast=true port=5000

# client
# gst-launch-1.0 -v udpsrc uri=udp://127.0.0.1:5000 caps="application/x-rtp,channels=(int)2,format=(string)S16LE,media=(string)audio,payload=(int)96,clock-rate=(int)44100,encoding-name=(string)L24" ! rtpL24depay ! audioconvert ! autoaudiosink sync=false


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
        sys.stderr.write("%s\n" % len(args))
        sys.stderr.write("usage: %s <port>\n" % args[0])
        sys.exit(1)

    #input_file_uri_str = args[1]
    output_port = int(args[1])

    # GObject.threads_init()
    Gst.init(None)

    pipeline = Gst.Pipeline()

    # if Gst.uri_is_valid(input_file_uri_str):
    #   uri = input_file_uri_str
    # else:
    #   uri = Gst.filename_to_uri(input_file_uri_str)

    src = Gst.ElementFactory.make("alsasrc", "alsasrc")
    # src = Gst.ElementFactory.make("filesrc", "filesrc")
    # src.set_property("location", input_file_uri_str)
    # demuxer = Gst.ElementFactory.make("oggdemux", "oggdemux")
    # parser = Gst.ElementFactory.make("mpegaudioparse", "mpegaudioparse")
    # decoder = Gst.ElementFactory.make("vorbisdec", "vorbisdec")
    # decoder = Gst.ElementFactory.make("mpg123audiodec", "mpg123audiodec")
    audioconvert = Gst.ElementFactory.make("audioconvert", "audioconvert")

    # udp
    rtpL24pay = Gst.ElementFactory.make("rtpL24pay", "rtpL24pay")
    sink = Gst.ElementFactory.make("udpsink", "udpsink")
    sink.set_property("host", "127.0.0.1") # TODO make configurable
    sink.set_property("auto-multicast", "true")
    sink.set_property("port", output_port) # TODO make configurable

    # speakers
    # audioresample = Gst.ElementFactory.make("audioresample", "audioresample")
    # sink = Gst.ElementFactory.make("autoaudiosink", "autoaudiosink")

    # output file
    # sink.set_property("location", output_file_url)

    pipeline.add(src)
    # pipeline.add(parser)
    # pipeline.add(decoder)
    pipeline.add(audioconvert)
    pipeline.add(rtpL24pay)
    pipeline.add(sink)

    src.link(audioconvert)
    # parser.link(decoder)
    # decoder.link(audioconvert)
    audioconvert.link(rtpL24pay)
    rtpL24pay.link(sink)

    # oggmux.link(sink)

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

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))


