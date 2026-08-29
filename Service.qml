import QtQuick
import Quickshell
import Quickshell.Io

// Keep all network and XML work outside omarchy-shell. The daemon owns a
// process lock, so plugin rescans cannot create duplicate pollers.
Item {
  id: root

  property var shell: null
  property bool active: true
  property string lastError: ""
  readonly property string backendPath: Qt.resolvedUrl("substack_backend.py").toString().replace(/^file:\/\//, "")

  function start() {
    if (root.active && !daemon.running) daemon.running = true
  }

  Process {
    id: daemon
    command: ["python3", root.backendPath, "daemon"]

    stderr: StdioCollector {
      waitForEnd: true
      onStreamFinished: {
        var message = String(text || "").trim()
        if (message !== "") root.lastError = message.substring(0, 240)
      }
    }

    onExited: function(exitCode) {
      if (!root.active) return
      if (exitCode !== 0) root.lastError = "Substack feed service exited with code " + exitCode
      restartTimer.restart()
    }
  }

  Timer {
    id: restartTimer
    interval: 4000
    repeat: false
    onTriggered: root.start()
  }

  Component.onCompleted: start()
  Component.onDestruction: {
    active = false
    restartTimer.stop()
    daemon.running = false
  }
}
