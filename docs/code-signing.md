# Code Signing Guide

This doc covers how to sign WOTT for macOS and Windows so users don't see security warnings when running the app.

---

## macOS

### What you need

- An **Apple Developer Program** membership ($99/year): https://developer.apple.com/programs/enroll/
- Xcode installed on your Mac (free from the App Store)

### Step 1: Get a Developer ID certificate

1. After enrolling, open **Xcode → Settings → Accounts** and sign in with your Apple ID.
2. Click **Manage Certificates → +** and choose **Developer ID Application**.
3. Xcode creates the certificate and installs it in your Keychain automatically.

### Step 2: Export the certificate

1. Open **Keychain Access**, find the certificate named `Developer ID Application: Your Name (TEAMID)`.
2. Expand it so both the certificate and its private key are visible, then select both.
3. Right-click → **Export 2 items** → save as `certificate.p12`.
4. Set a strong password — you'll need it as a GitHub secret.
5. Base64-encode it for storage:
   ```bash
   base64 -i certificate.p12 | pbcopy
   ```

### Step 3: Create an app-specific password

Apple requires an app-specific password (not your Apple ID password) for notarization:

1. Go to https://appleid.apple.com → **Sign-In and Security → App-Specific Passwords**.
2. Generate a new password, label it something like `wott-notarize`.
3. Save it — you won't be able to see it again.

### Step 4: Find your Team ID

Go to https://developer.apple.com/account → **Membership Details**. It's the 10-character alphanumeric string next to Team ID.

### Step 5: Add GitHub secrets

In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**. Add all five:

| Secret name | Value |
|---|---|
| `MACOS_CERTIFICATE` | Base64 string from Step 2 |
| `MACOS_CERTIFICATE_PWD` | Password you set on the .p12 |
| `APPLE_ID` | Your Apple ID email |
| `APPLE_ID_PASSWORD` | App-specific password from Step 3 |
| `APPLE_TEAM_ID` | 10-char Team ID from Step 4 |

### Step 6: Update the workflow

Replace the macOS build steps in `.github/workflows/build.yml` with:

```yaml
- name: Build with PyInstaller
  run: pyinstaller wott.spec

- name: Import certificate
  if: matrix.os == 'macos-latest'
  env:
    MACOS_CERTIFICATE: ${{ secrets.MACOS_CERTIFICATE }}
    MACOS_CERTIFICATE_PWD: ${{ secrets.MACOS_CERTIFICATE_PWD }}
  run: |
    echo "$MACOS_CERTIFICATE" | base64 --decode > certificate.p12
    security create-keychain -p actions build.keychain
    security default-keychain -s build.keychain
    security unlock-keychain -p actions build.keychain
    security import certificate.p12 -k build.keychain -P "$MACOS_CERTIFICATE_PWD" -T /usr/bin/codesign
    security set-key-partition-list -S apple-tool:,apple: -s -k actions build.keychain

- name: Sign the app
  if: matrix.os == 'macos-latest'
  env:
    APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
  run: |
    codesign --deep --force --options runtime \
      --sign "Developer ID Application: $(security find-certificate -c 'Developer ID Application' -p build.keychain | openssl x509 -noout -subject | sed 's/.*CN=//;s/,.*//')" \
      dist/WOTT.app

- name: Notarize the app
  if: matrix.os == 'macos-latest'
  env:
    APPLE_ID: ${{ secrets.APPLE_ID }}
    APPLE_ID_PASSWORD: ${{ secrets.APPLE_ID_PASSWORD }}
    APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
  run: |
    cd dist && zip -r WOTT-macOS.zip WOTT.app
    xcrun notarytool submit WOTT-macOS.zip \
      --apple-id "$APPLE_ID" \
      --password "$APPLE_ID_PASSWORD" \
      --team-id "$APPLE_TEAM_ID" \
      --wait
    xcrun stapler staple WOTT.app
    zip -r WOTT-macOS-signed.zip WOTT.app
    mv WOTT-macOS-signed.zip WOTT-macOS.zip

- name: Upload artifact (macOS)
  if: matrix.os == 'macos-latest'
  uses: actions/upload-artifact@v4
  with:
    name: WOTT-macOS
    path: dist/WOTT-macOS.zip
```

### How it works

- **Signing** embeds your identity in the app binary.
- **Notarization** submits the app to Apple's servers for malware scanning. Apple issues a ticket.
- **Stapling** attaches that ticket to the `.app` so macOS can verify it offline (no network needed at launch).

After all three steps, macOS opens the app without any security prompt.

---

## Windows

### What you need

An **OV (Organization Validated) code signing certificate** from a commercial CA. Recommended options:

- **DigiCert** — https://www.digicert.com/signing/code-signing-certificates (~$400/yr, reputable, good tooling)
- **Sectigo** — https://sectigo.com/ssl-certificates-tls/code-signing (~$200/yr, lower cost)

> **EV vs OV:** EV certificates ($400-700/yr) get immediate SmartScreen trust. OV certificates build trust over time as more users run the app — the SmartScreen warning fades after enough installs. For a personal project, OV is fine.

### Step 1: Purchase and validate

1. Buy the certificate from your chosen CA.
2. The CA will validate your identity (for OV, this is usually email/phone verification — no legal entity required for individuals on some CAs).
3. After validation, the CA issues a certificate file (`.pfx` or `.p12`).

### Step 2: Add GitHub secrets

| Secret name | Value |
|---|---|
| `WINDOWS_CERTIFICATE` | Base64-encoded `.pfx`: `base64 -i cert.pfx` |
| `WINDOWS_CERTIFICATE_PWD` | Password set on the `.pfx` |

### Step 3: Update the workflow

Add these steps after the PyInstaller build for Windows:

```yaml
- name: Sign the executable
  if: matrix.os == 'windows-latest'
  env:
    WINDOWS_CERTIFICATE: ${{ secrets.WINDOWS_CERTIFICATE }}
    WINDOWS_CERTIFICATE_PWD: ${{ secrets.WINDOWS_CERTIFICATE_PWD }}
  shell: pwsh
  run: |
    $certBytes = [Convert]::FromBase64String($env:WINDOWS_CERTIFICATE)
    [IO.File]::WriteAllBytes("certificate.pfx", $certBytes)
    & "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" sign `
      /f certificate.pfx `
      /p $env:WINDOWS_CERTIFICATE_PWD `
      /tr http://timestamp.digicert.com `
      /td sha256 `
      /fd sha256 `
      dist\WOTT.exe
    Remove-Item certificate.pfx
```

> The `signtool.exe` path may vary slightly by Windows SDK version on the runner. If it fails, check `C:\Program Files (x86)\Windows Kits\10\bin\` for the exact version folder.

### How it works

- Signing embeds your certificate in the `.exe`, proving it came from you and hasn't been tampered with.
- The timestamp (`/tr`) means the signature stays valid even after the certificate expires.
- SmartScreen checks the certificate against its reputation database. With OV, a warning may still appear for new apps until enough users have run it. With EV, no warning appears immediately.

---

## Workarounds (no certificate)

If you haven't set up signing yet and need users to run the app:

**macOS:**
```bash
xattr -dr com.apple.quarantine /path/to/WOTT.app
```
Or: right-click the app → Open → Open (bypasses Gatekeeper once).

**Windows:** Click "More info → Run anyway" on the SmartScreen dialog.
