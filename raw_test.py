import sys

import pyinotify


# Instanciate a new WatchManager (will be used to store watches).
wm = pyinotify.WatchManager()

# Associate this WatchManager with a Notifier (will be used to report and
# process events).
notifier = pyinotify.Notifier(wm)

# Add a new watch on /tmp for ALL_EVENTS.
wm.add_watch(sys.argv[1], pyinotify.ALL_EVENTS)
print('Watching: {0}'.format(sys.argv[1]))

# Loop forever and handle events.
notifier.loop()
