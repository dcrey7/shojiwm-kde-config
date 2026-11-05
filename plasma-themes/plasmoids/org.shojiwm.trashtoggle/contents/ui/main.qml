/*
 * The taskbar's recycle bin, as a toggle.
 *
 * KDE's own Trash widget opens trash:/ on every click and knows nothing
 * about the Dolphin window it opened, so a second click cannot minimize it.
 * This one looks for that window among the open windows first:
 *
 *   click ──> a Dolphin window showing the trash?
 *               ├─ no                      ──> open trash:/ in Dolphin
 *               ├─ yes, in front           ──> minimize it
 *               └─ yes, behind / minimized ──> bring it to the front
 *
 * The icon is full while ~/.local/share/Trash/files holds anything.
 */
import QtQuick
import QtQuick.Layouts
import QtCore
import Qt.labs.folderlistmodel
import org.kde.plasma.plasmoid
import org.kde.plasma.plasma5support as P5Support
import org.kde.kirigami as Kirigami
import org.kde.taskmanager as TaskManager

PlasmoidItem {
    id: root

    preferredRepresentation: fullRepresentation
    toolTipMainText: "Recycle Bin"
    toolTipSubText: trashFiles.count > 0 ? "Holds deleted files" : "Empty"
    readonly property string trashIcon: trashFiles.count > 0 ? "user-trash-full" : "user-trash"
    Plasmoid.icon: trashIcon


    // What is in the trash, only to pick the full or empty icon.
    FolderListModel {
        id: trashFiles
        folder: StandardPaths.writableLocation(StandardPaths.GenericDataLocation) + "/Trash/files"
        showDirs: true
        showHidden: true
        showDotAndDotDot: false
    }

    // Every window, one row each (no groups), on any screen or desktop.
    TaskManager.TasksModel {
        id: tasks
        groupMode: TaskManager.TasksModel.GroupDisabled
        filterByScreen: false
        filterByVirtualDesktop: false
        filterByActivity: false
    }

    // Runs Dolphin. Qt.openUrlExternally("trash:/") goes through xdg-open,
    // which has no handler for trash:, so KDE asked which app to use.
    P5Support.DataSource {
        id: launcher
        engine: "executable"
        onNewData: function(sourceName) {
            disconnectSource(sourceName)
        }
    }

    /** The row of a Dolphin window showing the trash, or -1. */
    function trashWindowRow() {
        for (let row = 0; row < tasks.rowCount(); ++row) {
            const index = tasks.makeModelIndex(row);
            const appId = String(tasks.data(index, TaskManager.AbstractTasksModel.AppId) || "");
            const title = String(tasks.data(index, Qt.DisplayRole) || "");
            // Dolphin names the window after the folder: "Trash — Dolphin".
            if (appId.indexOf("dolphin") !== -1
                    && (title.startsWith("Trash") || title.startsWith("trash:/"))) {
                return row;
            }
        }
        return -1;
    }

    function toggle() {
        const row = trashWindowRow();
        if (row < 0) {
            launcher.connectSource("dolphin --new-window trash:/");
            return;
        }
        const index = tasks.makeModelIndex(row);
        const active = tasks.data(index, TaskManager.AbstractTasksModel.IsActive);
        const minimized = tasks.data(index, TaskManager.AbstractTasksModel.IsMinimized);
        if (active && !minimized) {
            tasks.requestToggleMinimized(index);
        } else {
            tasks.requestActivate(index);
        }
    }

    // A square as tall as the panel, like the task icons next to it.
    fullRepresentation: Kirigami.Icon {
        id: button
        Layout.minimumWidth: height
        Layout.preferredWidth: height
        Layout.minimumHeight: Kirigami.Units.iconSizes.small
        source: root.trashIcon
        active: area.containsMouse

        MouseArea {
            id: area
            anchors.fill: parent
            hoverEnabled: true
            onClicked: root.toggle()
        }
    }
}
