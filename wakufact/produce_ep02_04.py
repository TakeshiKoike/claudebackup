#!/usr/bin/env python3
"""EP02〜EP04 バッチ制作"""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from batch_produce import produce_episode

# ============================================================
# EP02: あなたの脳は小さな電球1個分の電力で動いている
# ============================================================
EP02_SECTIONS = [
    {"key": "hook", "pause_ms": 800,
     "text": "世界最高のコンピュータは、たった20ワットで動いています。",
     "subtitle": "世界最高のコンピュータは、\\Nたった20ワットで動いています。"},
    {"key": "develop_1", "pause_ms": 500,
     "text": "それはあなたの脳。スマホの充電器より少ない電力で、860億個の脳の細胞が毎秒何兆回もの計算をしている。",
     "subtitle": "それはあなたの脳。\\Nスマホの充電器より少ない電力で、\\N860億個の脳の細胞が\\N毎秒何兆回もの計算をしている。"},
    {"key": "develop_2", "pause_ms": 600,
     "text": "同じことをスーパーコンピュータでやると、何百万ワットも必要です。",
     "subtitle": "同じことをスーパーコンピュータでやると、\\N何百万ワットも必要です。"},
    {"key": "develop_3", "pause_ms": 500,
     "text": "脳は体重のたった2パーセントなのに、体のエネルギーの20パーセントも使っている。めちゃくちゃ大食いなんです。",
     "subtitle": "脳は体重のたった2パーセントなのに、\\N体のエネルギーの20パーセントも使っている。\\Nめちゃくちゃ大食いなんです。"},
    {"key": "climax", "pause_ms": 1000,
     "text": "でもこの20ワットで、言葉を話し、夢を見て、宇宙の謎を考えられる。",
     "subtitle": "でもこの20ワットで、\\N言葉を話し、夢を見て、\\N宇宙の謎を考えられる。"},
    {"key": "cta", "pause_ms": 0,
     "text": "あなたの頭の中には、宇宙で最も効率的なマシンが入っています。フォローして次の雑学も見てね。",
     "subtitle": "あなたの頭の中には、\\N宇宙で最も効率的なマシンが\\N入っています。\\Nフォローして次の雑学も見てね。"},
]

EP02_IMAGES = [
    {"label": "01_hook", "prompt": "Professional food photography style, a single small glowing light bulb on a dark background, warm Edison bulb glow, everything sharp and in focus, deep focus f/16, studio lighting, vertical 9:16 format"},
    {"label": "02_intro", "prompt": "Professional photography, side view of a human head silhouette with glowing neural network visible inside the brain area, dark blue background, bright synapses, everything sharp and in focus, deep focus f/16, vertical format"},
    {"label": "03_develop_1", "prompt": "Professional photography, overhead flat lay comparison on dark surface: a small light bulb on the left next to a smartphone charger on the right, clean minimal composition, everything sharp and in focus, deep focus f/16, bright studio lighting, vertical format"},
    {"label": "04_develop_2", "prompt": "Professional photography, a large server room with rows of blinking servers and cables, blue LED lighting, wide angle shot showing the massive scale, everything sharp and in focus, deep focus f/16, vertical format"},
    {"label": "05_develop_3", "prompt": "Professional photography, a brain-shaped object made of colorful food items like fruits and vegetables on a white plate, creative food art, overhead flat lay, everything sharp and in focus, deep focus f/16, bright studio lighting, vertical format"},
    {"label": "06_climax", "prompt": "Professional photography, a person looking up at a starry night sky, silhouette shot with milky way visible, wide angle, everything sharp and in focus, deep focus f/16, long exposure style, vertical format"},
    {"label": "07_cta", "prompt": "Professional photography, a glowing brain model on a pedestal surrounded by small light bulbs, warm ambient lighting, everything sharp and in focus, deep focus f/16, vertical format"},
]

# ============================================================
# EP03: 宇宙はステーキとラム酒の匂いがする
# ============================================================
EP03_SECTIONS = [
    {"key": "hook", "pause_ms": 800,
     "text": "宇宙飛行士が宇宙服を脱いだ瞬間、焼肉の匂いがした。",
     "subtitle": "宇宙飛行士が宇宙服を脱いだ瞬間、\\N焼肉の匂いがした。"},
    {"key": "develop_1", "pause_ms": 500,
     "text": "宇宙から帰ってきて宇宙服を脱ぐと、焼けたステーキ、火薬、そしてラム酒の匂いがする。NASAも認めています。",
     "subtitle": "宇宙から帰ってきて宇宙服を脱ぐと、\\N焼けたステーキ、火薬、\\Nそしてラム酒の匂いがする。\\NNASAも認めています。"},
    {"key": "develop_2", "pause_ms": 600,
     "text": "この匂いの正体は、星が死ぬときに出す化学物質。つまり宇宙の匂いは、星の最後の香りなんです。",
     "subtitle": "この匂いの正体は、\\N星が死ぬときに出す化学物質。\\Nつまり宇宙の匂いは、\\N星の最後の香りなんです。"},
    {"key": "develop_3", "pause_ms": 500,
     "text": "ちなみにNASAは2020年に、この匂いを再現した香水のプロジェクトを応援しました。",
     "subtitle": "ちなみにNASAは2020年に、\\Nこの匂いを再現した香水の\\Nプロジェクトを応援しました。"},
    {"key": "climax", "pause_ms": 1000,
     "text": "宇宙の香り、嗅いでみたくないですか？",
     "subtitle": "宇宙の香り、\\N嗅いでみたくないですか？"},
    {"key": "cta", "pause_ms": 0,
     "text": "宇宙にはまだまだ不思議がいっぱい。フォローして次の雑学も見てね。",
     "subtitle": "宇宙にはまだまだ不思議がいっぱい。\\Nフォローして次の雑学も見てね。"},
]

EP03_IMAGES = [
    {"label": "01_hook", "prompt": "Professional photography, an astronaut in a white spacesuit floating in space with Earth visible in the background, dramatic lighting, everything sharp and in focus, deep focus f/16, cinematic, vertical 9:16 format"},
    {"label": "02_intro", "prompt": "Professional photography, an astronaut inside a space station removing their helmet, warm interior lighting, everything sharp and in focus, deep focus f/16, vertical format"},
    {"label": "03_develop_1", "prompt": "Professional food photography, a grilled ribeye steak on a plate next to a glass of dark rum, wisps of smoke rising, on a dark wooden table, everything sharp and in focus, deep focus f/16, warm lighting, vertical format"},
    {"label": "04_develop_2", "prompt": "Professional photography, a beautiful nebula in deep space with colorful gas clouds in purple orange and blue, stars scattered throughout, Hubble telescope style, everything sharp and in focus, vertical format"},
    {"label": "05_develop_3", "prompt": "Professional photography, an elegant perfume bottle with a cosmic galaxy design inside it, on a reflective dark surface with small stars, everything sharp and in focus, deep focus f/16, studio lighting, vertical format"},
    {"label": "06_climax", "prompt": "Professional photography, a person standing in a field at night looking up at a vivid milky way galaxy, wide angle shot, silhouette, everything sharp and in focus, deep focus f/16, vertical format"},
    {"label": "07_cta", "prompt": "Professional photography, planet Earth seen from space with the sun rising on the horizon creating a bright golden glow, everything sharp and in focus, deep focus, vertical format"},
]

# ============================================================
# EP04: ハチミツは3000年経っても腐らない
# ============================================================
EP04_SECTIONS = [
    {"key": "hook", "pause_ms": 800,
     "text": "エジプトのピラミッドから見つかったハチミツ、まだ食べられた。",
     "subtitle": "エジプトのピラミッドから見つかった\\Nハチミツ、まだ食べられた。"},
    {"key": "develop_1", "pause_ms": 500,
     "text": "ピラミッドから3000年前のハチミツが見つかりました。驚くことに、まだ食べられる状態だったんです。",
     "subtitle": "ピラミッドから3000年前のハチミツが\\N見つかりました。\\N驚くことに、\\Nまだ食べられる状態だったんです。"},
    {"key": "develop_2", "pause_ms": 600,
     "text": "ハチミツが腐らない理由は3つ。まず水分がすごく少ない。バイキンが生きられない。そして強い酸性。",
     "subtitle": "ハチミツが腐らない理由は3つ。\\Nまず水分がすごく少ない。\\Nバイキンが生きられない。\\Nそして強い酸性。"},
    {"key": "develop_3", "pause_ms": 500,
     "text": "さらにミツバチの出す成分が、天然の消毒液を作り出す。ハチミツは自分で自分を守っているんです。",
     "subtitle": "さらにミツバチの出す成分が、\\N天然の消毒液を作り出す。\\Nハチミツは自分で自分を\\N守っているんです。"},
    {"key": "climax", "pause_ms": 1000,
     "text": "古代エジプト人はハチミツを傷薬に使っていました。3000年後の科学がそれを正しいと証明した。",
     "subtitle": "古代エジプト人はハチミツを\\N傷薬に使っていました。\\N3000年後の科学が\\Nそれを正しいと証明した。"},
    {"key": "cta", "pause_ms": 0,
     "text": "自然は最初から答えを知っていたんです。フォローして次の雑学も見てね。",
     "subtitle": "自然は最初から答えを\\N知っていたんです。\\Nフォローして次の雑学も見てね。"},
]

EP04_IMAGES = [
    {"label": "01_hook", "prompt": "Professional photography, the Great Pyramids of Giza in golden sunset light, clear sky, everything sharp and in focus, deep focus f/16, wide angle, dramatic lighting, vertical 9:16 format"},
    {"label": "02_intro", "prompt": "Professional photography, an ancient Egyptian clay pot filled with golden honey, placed on sand with pyramid silhouettes in the background, warm golden lighting, everything sharp and in focus, deep focus f/16, vertical format"},
    {"label": "03_develop_1", "prompt": "Professional food photography, a glass jar of golden honey with a wooden honey dipper, honeycomb pieces beside it on a light wooden table, warm lighting, everything sharp and in focus, deep focus f/16, overhead flat lay, vertical format"},
    {"label": "04_develop_2", "prompt": "Professional photography, honeybees working on a honeycomb frame, golden hexagonal cells filled with honey, several bees visible, bright natural lighting, everything sharp and in focus, deep focus f/16, vertical format"},
    {"label": "05_develop_3", "prompt": "Professional photography, close view of a honeycomb dripping golden honey onto a white surface, with a few bees nearby, bright warm studio lighting, everything sharp and in focus, deep focus f/16, vertical format"},
    {"label": "06_climax", "prompt": "Professional photography, ancient Egyptian wall painting style scene showing a person applying golden substance to a wound, warm amber tones, museum lighting, everything sharp and in focus, deep focus f/16, vertical format"},
    {"label": "07_cta", "prompt": "Professional photography, a beautiful honey jar surrounded by wildflowers and honeycomb pieces, golden warm lighting, nature background, everything sharp and in focus, deep focus f/16, vertical format"},
]


if __name__ == "__main__":
    episodes = [
        (2, "あなたの脳は\\N小さな電球1個分の電力で動いている", EP02_SECTIONS, EP02_IMAGES),
        (3, "宇宙はステーキと\\Nラム酒の匂いがする", EP03_SECTIONS, EP03_IMAGES),
        (4, "ハチミツは\\N3000年経っても腐らない", EP04_SECTIONS, EP04_IMAGES),
    ]

    # 引数でエピソード指定可能
    if len(sys.argv) > 1:
        nums = [int(x) for x in sys.argv[1:]]
        episodes = [ep for ep in episodes if ep[0] in nums]

    for ep_num, title, sections, images in episodes:
        produce_episode(ep_num, title, sections, images)

    print("\n\n=== ALL EPISODES DONE ===")
