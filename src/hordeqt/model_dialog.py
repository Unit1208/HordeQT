from hordeqt.gen.ui_modelinfo import Ui_Dialog
from PySide6.QtWidgets import QDialog


class ModelPopup(QDialog):

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)

        self.ui: Ui_Dialog = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.baselineLineEdit.setText(data.get("baseline", "stable_diffusion_xl"))
        self.ui.nameLineEdit.setText(data.get("name", "AlbedoBase XL (SDXL)"))
        self.ui.inpaintingCheckBox.setChecked(data.get("inpainting", False))
        self.ui.descriptionBox.setText(
            data.get("description", "SDXL Model that doesn't require a refiner")
        )
        self.ui.versionLineEdit.setText(data.get("version", "2.1"))
        self.ui.styleLineEdit.setText(data.get("style", "generalist"))
        self.ui.nsfwCheckBox.setChecked(data.get("nsfw", False))
        self.ui.unsupportedFeaturesLineEdit.setText(
            ", ".join(data.get("features_not_supported", []))
        )
        req: dict = data.get("requirements", {})
        req_str = ", ".join(" = ".join([str(y) for y in x]) for x in list(req.items()))
        self.ui.requirementsLineEdit.setText(req_str)
