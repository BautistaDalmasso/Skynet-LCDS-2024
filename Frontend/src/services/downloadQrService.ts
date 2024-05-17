import * as FileSystem from "expo-file-system";

import { ServerAddress } from "../common/consts/serverAddress";
import { IUser } from "../common/interfaces/User";
import { IQrCodeInfo, QrToggle } from "../common/interfaces/QrCodeInfo";

export class DownloadQrService {
  private static baseRoute: string = `${ServerAddress}qr`;

  static async updateQrCode(
    lastUser: IUser | null,
    lastQrCodeInfo: IQrCodeInfo | null,
    token: string,
    qrToggle: QrToggle,
  ): Promise<boolean> {
    if (lastUser === null) {
      throw Error("User hasn't logged in properly.");
    }

    // No qr code has been downloaded, or last qr code downloaded wasn't for this user
    // or last qr code downloaded requires an update.
    if (
      lastQrCodeInfo === null ||
      lastUser.email !== lastQrCodeInfo.userEmail ||
      lastUser.lastPermissionUpdate !== lastQrCodeInfo.lastUpdate
    ) {
      await this.downloadQr(token, qrToggle);

      return true;
    }

    return false;
  }

  static async downloadQr(token: string, toggle: QrToggle) {
    return FileSystem.downloadAsync(
      DownloadQrService.baseRoute,
      FileSystem.documentDirectory + toggle + "qr.png",
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );
  }
}
