# Birth Flower

A birthday greeting, grown one petal at a time. This personal keepsake combines a cotton rose with a Python-rendered animation and a small interactive web preview.

**[Open the project website](https://morhsophie.github.io/Birth-flower/)** · [View the source on GitHub](https://github.com/Morhsophie/Birth-flower)

## The project

The animation is rendered frame by frame with Pillow, then assembled into an MP4 with ImageIO and FFmpeg. The flower is the cotton rose, associated here with delicate beauty.

The static landing page includes a small browser preview where you can personalize the greeting and replay the flower reveal. It runs without a build step or JavaScript framework.

## Run the animation

Requires Python 3.9 or newer.

```powershell
python -m pip install -r requirements.txt
python birth_flower.py --name "Your Name"
```

By default, the script reads `Cotton Rose.png` and writes `Cotton Rose_anim.mp4` in the current directory. Customize the greeting with command-line options:

```powershell
python birth_flower.py --name "Your Name" --date "November 11" --flower "Cotton Rose" --meaning "Delicate Beauty"
```

Run `python birth_flower.py --help` to see all available options.

## Run the website locally

Open `index.html` in a browser, or serve the project folder with Python:

```powershell
python -m http.server 8000
```

Then visit `http://localhost:8000`.

## Publish with GitHub Pages

In the repository, open **Settings → Pages** and set the source to **GitHub Actions**. The included workflow publishes the site after each push to `main`. The first deployment may take a few minutes; its status and live URL appear under the repository's **Actions** tab. GitHub Pages will publish the landing page at the project website link above.

## Built with

- Python
- Pillow
- NumPy
- ImageIO and FFmpeg
- HTML, CSS, and vanilla JavaScript
