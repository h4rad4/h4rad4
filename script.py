import requests
import os
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import time

USERNAME = "h4rad4"
TOKEN = os.getenv("GITHUB_TOKEN")

BIRTHDAY = date(2003, 10, 30)

BLUE = "#58a6ff"
BLUE_LIGHT = "#58a6ff"
GRAY = "#c9d1d9"
GRAY_DARK = "#8b949e"
GREEN = "#3fb950"
RED = "#f85149"
ORANGE = "#d29922"
BG = "#0d1117"
ASCII_BLUE = "#58a6ff"

ASCII_ART = """;;;;;;;;;;;;;;;i11i;;i1ffftii11t1i;iiiiiiiiiiiiii111
;;;;;;;;;;;;;;1LCLi;:;i;,,,::iCGGGLi;iiiiiiiiiiii111
;;;;;;;;;;;;;f0GGCCGGGCfLt;;i1tG888G1;iiiiiiiiiii111
;;;;;;;;;;;iL0G000080CffCf11tG008888Gi;iiiiiiiiiii11
;;;;;;;;;;iC0GG00880Cff1tftfC08888888C;;iiiiiiiiii11
;;;;;;;;;;fG0008000Cft1iitLGGGG0888888t;iiiiiiiiii11
;;;;;;;;;;L8880GGGCLfttfLCGGGGLC888888C;iiiiiiiiii11
;;;;;;;;;:f80GCGCLLLffLCCGCCCCCCC08088L;;iiiiiiiii11
;;;;;;;;;;108Ctt11ttfttttttffffftffC@81;iiiiiiiiii11
;;;;;;;;;;;C8L1tfLGGCLtttffLCCGGCftf8C;;iiiiiiiiii11
;;;;;;;;;;;t011tftfLLft1:tfLLLLLLLLftCt;;;iiiiiiiii1
;;;;;;;;;;;tC;;i11tt1ti. :1fttttttttLf;;;iiiiiiiii11
;;;;;;;;;;;;f1ii1111ti;;;i1tftttttt1Lt;;;iiiiiiiii11
;;;;;;;;;;;;tt11i11tt1LftfCfffttttt1fi;;iiiiiiiii111
;;;;;;;;;;;;i1111ii1i1ttffffffttttttti;;;iiiiiiii111
;;;;;;;;;;;;;;i111iiiittffftttttt11i;;;;iiiiiiiii111
;;;;;;;;;;;;;;;1111tffffLLLLLftttt1;;;;;iiiiiiiii111
;;;;;;;;;;;;;;;i1111t11tttttttttt1i;;;;iiiiiiiii1111
;;;;;;;;;;;;;;;;i1t1111tttttttttti;;;;iiiiiiiiii1111
iiii;;;;;;;;;;;;;1tt1111ttttttfft1;;;;iiiiiiiiii1111
iiiiiiiii;;;;;;ifLttttttttttfffffGGLft1iiiiiiii11111
iiiiiiiiiii11tfG8fftttttttfffffffG@@880GCft1iiii111t
iiiiii11tffLLLC08LtftttttttttfffL8@88888@@80GCLftttt
1ttffffffffffLG88GftfttttttttfffG88888888888800GLLff
LLLfffffffLfLC0880LftfttttttfffLG88888888888880GCCLL
fLLLffLffLLfLCG088GfffttttttfLLLG@88888888888800GCCL
LLLLLLLLfLLLLGG0888CfttfftttfffC8888888888888880GCCL
CCCLLLLLLLLLCGG00888GfttttttffC88888888888888880GGCC"""


def calculate_uptime():
    today = date.today()
    delta = relativedelta(today, BIRTHDAY)
    return f"{delta.years} years, {delta.months} months, {delta.days} days"



def get_headers():
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": USERNAME
    }
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    return headers



def fetch_github_stats():
    query = """
    query($username: String!) {
        user(login: $username) {
            name
            contributionsCollection {
                totalCommitContributions
                restrictedContributionsCount
                contributionCalendar {
                    totalContributions
                }
            }
            repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
                totalCount
                nodes {
                    name
                    stargazerCount
                    isPrivate
                    primaryLanguage {
                        name
                    }
                }
            }
            repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, PULL_REQUEST, REPOSITORY]) {
                totalCount
            }
            followers {
                totalCount
            }
            following {
                totalCount
            }
        }
    }
    """
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    } if TOKEN else {"Content-Type": "application/json"}
    
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"username": USERNAME}},
        headers=headers
    )
    data = response.json()
    return data.get("data", {}).get("user", {})



def fetch_repo_stats(repo_name):
        url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/stats/contributors"
        response = requests.get(url, headers=get_headers())
        
        if response.status_code == 202:
            import time
            time.sleep(2)
            response = requests.get(url, headers=get_headers())
        
        if response.status_code != 200:
            return {"additions": 0, "deletions": 0}
        
        data = response.json()
        if not data:
            return {"additions": 0, "deletions": 0}
        
        total_additions = 0
        total_deletions = 0
        
        for contributor in data:
            if contributor.get("author", {}).get("login", "").lower() == USERNAME.lower():
                for week in contributor.get("weeks", []):
                    total_additions += week.get("a", 0)
                    total_deletions += week.get("d", 0)
        
        return {"additions": total_additions, "deletions": total_deletions}
    
    
    
def fetch_all_repos_stats(repo_names):
    total_additions = 0
    total_deletions = 0
    
    print(f"Fetching stats for {len(repo_names)} repositories...")
    
    for i, repo in enumerate(repo_names):
        stats = fetch_repo_stats(repo)
        total_additions += stats["additions"]
        total_deletions += stats["deletions"]
        print(f"  [{i+1}/{len(repo_names)}] {repo}: +{stats['additions']:,} / -{stats['deletions']:,}")
        
        time.sleep(0.5)

    return {
        "additions": total_additions,
        "deletions": total_deletions,
        "total": total_additions - total_deletions
    }



def format_number(n):
    return f"{n:,}"



def generate_svg(stats, loc_stats):
    if not stats:
        stats = {
            "name": "h4rad4",
            "contributionsCollection": {
                "totalCommitContributions": 0,
                "contributionCalendar": {"totalContributions": 0}
            },
            "repositories": {"totalCount": 0, "nodes": []},
            "repositoriesContributedTo": {"totalCount": 0},
            "followers": {"totalCount": 0},
            "following": {"totalCount": 0}
        }
    
    commits = stats.get("contributionsCollection", {}).get("totalCommitContributions", 0)
    repos = stats.get("repositories", {}).get("totalCount", 0)
    contributed_to = stats.get("repositoriesContributedTo", {}).get("totalCount", 0)
    total_stars = sum(repo.get("stargazerCount", 0) for repo in stats.get("repositories", {}).get("nodes", []))
    followers = stats.get("followers", {}).get("totalCount", 0)
    
    loc_total = loc_stats.get("total", 0)
    loc_additions = loc_stats.get("additions", 0)
    loc_deletions = loc_stats.get("deletions", 0)
    
    uptime = calculate_uptime()
    
    ascii_lines = ASCII_ART.split('\n')
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="920" height="560" viewBox="0 0 920 560">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&amp;display=swap');
        
        .bg {{ fill: {BG}; }}
        
        .ascii {{ 
        font: 500 12px 'JetBrains Mono', monospace; 
        fill: {ASCII_BLUE};
        animation: glow 3s ease-in-out infinite alternate;
        }}
        
        .label {{ 
        font: 400 13px 'JetBrains Mono', monospace; 
        fill: {ORANGE}; 
        }}
        
        .value {{ 
        font: 400 13px 'JetBrains Mono', monospace; 
        fill: {GRAY}; 
        text-anchor: end; 
        }}
        
        .dots {{ font: 400 13px 'JetBrains Mono', monospace; fill: {GRAY_DARK}; }}
        
        .header {{ 
        font: 700 14px 'JetBrains Mono', monospace; 
        fill: {BLUE_LIGHT};
        animation: pulse 2s ease-in-out infinite;
        }}
        
        .section {{ font: 400 13px 'JetBrains Mono', monospace; fill: {GRAY_DARK}; }}
        .green {{ font: 400 13px 'JetBrains Mono', monospace; fill: {GREEN}; }}
        .red {{ font: 400 13px 'JetBrains Mono', monospace; fill: {RED}; }}
        .quote {{ font: 400 13px 'JetBrains Mono', monospace; fill: {GRAY}; font-style: italic; }}
        .author {{ font: 400 13px 'JetBrains Mono', monospace; fill: {GRAY_DARK}; }}
        
        
        @keyframes glow {{
        from {{
            filter: drop-shadow(0 0 3px {ASCII_BLUE});
        }}
        to {{
            filter: drop-shadow(0 0 10px {ASCII_BLUE}) drop-shadow(0 0 20px {ASCII_BLUE});
        }}
        }}
        
        @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
        }}
    </style>
    
    
    <defs>
        <linearGradient id="scanline" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" style="stop-color:{ASCII_BLUE};stop-opacity:0" />
        <stop offset="50%" style="stop-color:{ASCII_BLUE};stop-opacity:1" />
        <stop offset="100%" style="stop-color:{ASCII_BLUE};stop-opacity:0" />
        </linearGradient>
    </defs>
    
    <rect class="bg" width="920" height="560" rx="8"/>
    
    <!-- ASCII Art -->
    <g transform="translate(45, 45)">
        <text class="ascii" x="0" y="0">
    '''
    
    for i, line in enumerate(ascii_lines):
        escaped_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        if i == 0:
            svg += f'      <tspan x="0" dy="0">{escaped_line}</tspan>\n'
        else:
            svg += f'      <tspan x="0" dy="14.5">{escaped_line}</tspan>\n'
    
    svg += f'''    </text>
    </g>
    
    <!-- Info Section -->
    <g transform="translate(470, 55)">
        <!-- Header -->
        <text class="header" x="0" y="0">{USERNAME}@github</text>
        <text class="dots" x="0" y="20">────────────────────────────────────────────────────────</text>
        
        <!-- System Info -->
        <g>
        <text class="label" x="0" y="50">Role</text>
        <text class="dots" x="32" y="50">: .................................</text>
        <text class="value" x="405" y="50">Computer Engineer</text>
        </g>
        
        <g>
        <text class="label" x="0" y="72">Uptime</text>
        <text class="dots" x="44" y="72">: .....................</text>
        <text class="value" x="405" y="72">{uptime}</text>
        </g>
        
        <g>
        <text class="label" x="0" y="94">Exploring</text>
        <text class="dots" x="68" y="94">: ................</text>
        <text class="value" x="405" y="94">Deep Learning, Expert Systems</text>
        </g>
        
        <!-- Languages -->
        <g>
        <text class="label" x="0" y="134">Languages.Computer</text>
        <text class="dots" x="130" y="134">: .....</text>
        <text class="value" x="405" y="134">Python, C/C++, Java, Kotlin, JS</text>
        </g>
        
        <g>
        <text class="label" x="0" y="156">Languages.Human</text>
        <text class="dots" x="114" y="156">: .........</text>
        <text class="value" x="405" y="156">Portuguese, English, Japanese</text>
        </g>
        
        <!-- Interests -->
        <g>
        <text class="label" x="0" y="196">Interests.AI</text>
        <text class="dots" x="90" y="196">: ............ </text>
        <text class="value" x="405" y="196">Knowledge Representation, LLMs</text>
        </g>
        
        <g>
        <text class="label" x="0" y="218">Interests.Hobbies</text>
        <text class="dots" x="120" y="218">: ....................</text>
        <text class="value" x="405" y="218">Minecraft Modding</text>
        </g>
        
        
        <!-- GitHub Stats -->
        <text class="section" x="0" y="288">— GitHub Stats</text>
        
        <g>
        <text class="label" x="0" y="315">Repos</text>
        <text class="dots" x="38" y="315">: ............</text>
        <text class="value" x="158" y="315">{repos}</text>
        <text class="dots" x="162" y="315">{{Contributed: {contributed_to}}}</text>
        <text class="label" x="280" y="315">| Stars</text>
        <text class="dots" x="327" y="315">: ....</text>
        <text class="value" x="405" y="315">{total_stars}</text>
        </g>
        
        <g>
        <text class="label" x="0" y="337">Commits</text>
        <text class="dots" x="50" y="337">: ..........</text>
        <text class="value" x="158" y="337">{format_number(commits)}</text>
        <text class="label" x="280" y="337">| Followers</text>
        <text class="dots" x="350" y="337">:</text>
        <text class="value" x="405" y="337">{followers}</text>
        </g>
        
        <g>
        <text class="label" x="0" y="359">Lines of Code</text>
        <text class="dots" x="98" y="359">: ...... </text>
        <text class="value" x="200" y="359">{format_number(loc_total)}</text>
        <text class="dots" x="204" y="359">(</text>
        <text class="green" x="210" y="359">{format_number(loc_additions)}++</text>
        <text class="dots" x="285" y="359">,</text>
        <text class="red" x="294" y="359">{format_number(loc_deletions)}--</text>
        <text class="dots" x="365" y="359">)</text>
        </g>
    </g>
    
    <g transform="translate(45, 475)">
        <text class="dots" x="0" y="0">───────────────────────────────────────────────────────────────────────────────────────────────────────────────────</text>
        <text x="0" y="28">
        <tspan class="quote" x="0">"In God we trust. All others must bring data."</tspan>
        <tspan class="author">  — William E. Deming</tspan>
        </text>
    </g>
    
    <rect width="920" height="2" fill="url(#scanline)" opacity="0.3">
        <animateTransform
        attributeName="transform"
        type="translate"
        from="0 0"
        to="0 560"
        dur="3s"
        repeatCount="indefinite"/>
    </rect>
    
    </svg>'''
    
    return svg



def main():
    print(f"Fetching stats for {USERNAME}...")

    stats = fetch_github_stats()
    
    repo_names = []
    if stats:
        repo_names = [repo.get("name") for repo in stats.get("repositories", {}).get("nodes", []) if repo.get("name")]
    
    if repo_names:
        loc_stats = fetch_all_repos_stats(repo_names)
    else:
        loc_stats = {"additions": 0, "deletions": 0, "total": 0}
    
    
    print("\nGenerating SVG...")
    svg_content = generate_svg(stats, loc_stats)
    
    with open("profile.svg", "w", encoding="utf-8") as f:
        f.write(svg_content)
    
    print("Done!")


if __name__ == "__main__":
    main()