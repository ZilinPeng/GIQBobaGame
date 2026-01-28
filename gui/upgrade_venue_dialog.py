from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt


class UpgradeVenueDialog(QDialog):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.setWindowTitle("Upgrade Venue")
        self.setMinimumWidth(320)

        layout = QVBoxLayout(self)

        next_venue, cost = game.get_next_venue_upgrade()

        if not next_venue:
            layout.addWidget(QLabel("<b>Venue is already at maximum level.</b>"))
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(self.accept)
            layout.addWidget(close_btn)
            return

        info = QLabel(
            f"<b>Upgrade Available</b><br><br>"
            f"Current Venue: {game.venue.name}<br>"
            f"Next Venue: <b>{next_venue.name}</b><br><br>"
            f"Max Line: {game.venue.maxLine} → {next_venue.maxLine}<br>"
            f"Foot Traffic: {game.venue.footTraffic} → {next_venue.footTraffic}<br>"
            f"Base Patience: {game.venue.basePatience} → {next_venue.basePatience}<br>"
            f"Rent: ${game.venue.rent} → ${next_venue.rent}<br><br>"
            f"<b>Upgrade Cost:</b> ${cost}<br>"
            f"<b>Cash Available:</b> ${game.cash:.2f}"
        )
        info.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(info)

        upgrade_btn = QPushButton("Upgrade Venue")
        upgrade_btn.clicked.connect(self.try_upgrade)
        layout.addWidget(upgrade_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

    def try_upgrade(self):
        success, msg = self.game.upgrade_venue()
        if success:
            self.accept()