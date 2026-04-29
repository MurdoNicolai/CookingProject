from reactpy import component, html, hooks

from django.contrib.staticfiles import finders
@component
def RecipeBrowser():
    selected_recipe, set_selected_recipe = hooks.use_state(None)

    filters = {
        "ingredient": ["Wheat", "Wheat"],
        "geography": ["Wheat", "Wheat"],
        "season": ["Wheat", "Wheat"],
        "type": ["Wheat", "Wheat"],
        "other": ["Wheat", "Wheat"],
    }

    SVG_PATH = finders.find("images/Detailed leaf logo.svg")

    with open(SVG_PATH, "r", encoding="utf-8") as f:
        LOGO_SVG = f.read()

    recipes = [
        {
            "id": 1,
            "name": "Pork Belly Buns with Spicy Mayo, Scallions, and Pickled Bean Sprouts",
            "image": "🍔",
            "hasVideo": True,
            "hasPdf": True,
        },
        {
            "id": 2,
            "name": "Pineapple Toast with Caramelised Rum Bananas",
            "image": "🍍",
            "hasVideo": True,
            "hasPdf": True,
        },
        {
            "id": 3,
            "name": "Pickled Onion and Black Bean Tacos",
            "image": "🌮",
            "hasVideo": True,
            "hasPdf": True,
        },
        {
            "id": 4,
            "name": "Matcha Swiss Roll with Lemon Cream and Red Berries",
            "image": "🍰",
            "hasVideo": False,
            "hasPdf": True,
        },
    ]

    recipe_detail = {
        "title": "Pickled Jalapeño and Cream Cheese Quesadillas",
        "geography": "Mexico, North America",
        "allergens": "Vegetarian, contains dairy",
        "season": "All",
        "yields": "4 servings",
        "type": "Main dish, snack",
        "cookingTime": "15 minutes (Prep time: 5 minutes)",
        "ingredients": [
            "8 tortillas",
            "½ cup (75 grams) diced pickled jalapeño",
            "½ cup (50 grams) shredded cheddar cheese",
            "Salt and pepper to taste",
            "Sour cream and cilantro, for garnish",
        ],
        "method": [
            "Mix cream cheese, jalapeño, cheddar, salt and pepper.",
            "Spread on tortilla and fold.",
            "Cook 2–3 minutes each side until golden.",
            "Serve hot with garnish.",
        ],
    }

    # -------------------------
    # Components
    # -------------------------

    @component
    def RecipeCard(recipe):
        return html.div(
            {
                "class": "bg-beige-50 rounded-lg overflow-hidden cursor-pointer hover:shadow-md transition-shadow"
            },
            html.div(
                {
                    "class": "h-36 bg-orange-200 rounded-t-lg flex items-center justify-center text-5xl"
                },
                recipe["image"],
            ),
            html.div(
                {
                    "class": "flex items-center justify-center text-sm text-center px-2"
                },
                recipe["name"],
            ),
        )

    # Build filter pills
    filter_pills = []
    for filter_list in filters.values():
        for filter_val in filter_list:
            filter_pills.append(
                html.div(
                    {"class": "flex items-center px-4 py-2 bg-beige-100 border border-amber-900 rounded-lg"},
                    html.span(filter_val),
                    html.button({"class": "hover:text-red-600 ml-1"}, "×"),
                )
            )

    # Build filter selects
    filter_selects = []
    for label in ["Geography", "Season", "Type", "Other filters"]:
        filter_selects.append(
            html.select(
                {"class": "px-4 py-2 bg-beige-100 border border-amber-900 rounded-lg text-sm"},
                html.option(label),
            )
        )

    # -------------------------
    # Page Layout
    # -------------------------

    return html.div(
        {"class": "bg-beige-50 h-screen flex flex-col"},

        # Hide native scrollbars on both panels, style the fake thumbs
        html.style("""
            .hide-scroll {
                scrollbar-width: none;        /* Firefox */
                -ms-overflow-style: none;     /* IE/Edge */
            }
            .hide-scroll::-webkit-scrollbar {
                display: none;                /* Chrome/Safari */
            }
            .fake-thumb {
                position: absolute;
                width: 5px;
                background-color: #DBF5EF;
                border-radius: 10px;
                border: 1px solid #62706D;
                height: 80px;
                cursor: pointer;
                left: 0;
                top: 0;
            }
            .fake-track {
                position: relative;
                width: 8px;
                flex-shrink: 0;
                margin-left: 4px;
            }
        """),

        # ================= HEADER =================
        html.header(
            {"class": "min-h-32 relative pr-12 flex-shrink-0"},
            html.div(
                {"class": "flex justify-between items-center"},

                # Logo
                html.img({
                    "src": "/static/images/Detailed leaf logo.svg",
                    "alt": "Logo",
                    "class": "absolute top-0 left-4 h-40 w-auto z-0"
                }),

                html.div({"class": "pl-40"}),  # Space for logo

                # Filters grid
                html.div(
                    {"class": "px-6 py-4 flex-1 min-w-0"},
                    html.div(
                        {"class": "grid grid-cols-5 gap-2 auto-rows-max"},

                        # Search input
                        html.div(
                            {"class": "relative"},
                            html.img({
                                "src": "/static/images/search.svg",
                                "class": "absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5",
                                "alt": "Search Icon"
                            }),
                            html.input({
                                "type": "text",
                                "placeholder": "Ingredient",
                                "class": "w-full pl-10 pr-4 py-2 bg-beige-100 border border-amber-900 rounded-lg"
                            })
                        ),

                        *filter_selects,
                        *filter_pills,
                    )
                ),

                # Login
                html.button(
                    {"class": "w-44 h-14 text-center text-black text-base bg-green-100 border border-teal-900 rounded-[20px] hover:bg-teal-300 transition-colors"},
                    "Login",
                ),
            )
        ),

        # ================= MAIN =================
        html.div(
            {"class": "flex-1 flex px-12 gap-4 min-h-0 pb-4"},

            # -------- LEFT PANEL (GRID) --------
            html.div(
                {"class": "w-1/2 flex flex-col gap-4 min-h-0"},

                # Search bar
                html.div(
                    {"class": "flex-shrink-0 flex gap-4 items-center py-3"},
                    html.div(
                        {"class": "relative flex items-center flex-1"},
                        html.img({
                            "src": "/static/images/search.svg",
                            "class": "absolute left-3 w-5 h-5",
                            "alt": "Search"
                        }),
                        html.input({
                            "type": "text",
                            "placeholder": "Search recipes",
                            "class": "w-full h-10 pl-10 bg-beige-100 rounded-lg border border-yellow-900 text-base",
                        })
                    ),
                    html.button(
                        {"class": "h-10 aspect-square rounded-lg border border-yellow-900 bg-beige-100 shadow-md hover:shadow-sm active:shadow-none active:translate-y-0.5 transition-all"},
                        "♥️",
                    ),
                ),

                # +++ CHANGED: wrap grid + fake scrollbar in a flex row +++
                html.div(
                    {"class": "flex-1 flex min-h-0"},

                    # Scrollable grid — native bar hidden
                    html.div(
                        {
                            "class": "flex-1 grid grid-cols-4 gap-6 overflow-y-scroll min-h-0 auto-rows-max hide-scroll",
                            "id": "grid-scroll"
                        },
                        *[RecipeCard(recipe) for recipe in recipes * 3],
                    ),
                    # Fake scrollbar track
                    html.div(
                        {"class": "fake-track", "id": "grid-track"},
                        html.div({"class": "fake-thumb", "id": "grid-thumb"}),
                    ),
                ),
            ),

            # -------- RIGHT PANEL (DETAIL) --------
            html.div(
                {"class": "w-1/2 flex min-h-0 bg-beige-200 rounded-lg shadow-md border border-black"},

                # Scrollable content
                html.div(
                    {"class": "flex-1 flex gap-6 flex-col overflow-y-scroll min-h-0 p-6 pr-0 hide-scroll", "id": "detail-scroll"},

                    # Top section: info + image + buttons
                    html.div(
                        {"class": "flex-shrink-0 flex gap-6"},

                        # Left column: title + metadata + ingredients
                        html.div(
                            {"class": "w-1/2 flex flex-col flex-1 gap-4"},

                            html.h2(
                                {"class": "text-xl font-bold"},
                                f"Recipe: {recipe_detail['title']}",
                            ),

                            html.div(
                                {"class": "text-sm space-y-2"},
                                html.p(f"Geography: {recipe_detail['geography']}"),
                                html.p(f"Allergens/diet: {recipe_detail['allergens']}"),
                                html.p(f"Season: {recipe_detail['season']}"),
                                html.p(f"Yields: {recipe_detail['yields']}"),
                                html.p(f"Type: {recipe_detail['type']}"),
                                html.p(f"Cooking Time: {recipe_detail['cookingTime']}"),
                            ),

                            # Ingredients
                            html.div(
                                {"class": "bg-beige-100 rounded-lg border border-amber-900 p-4 drop-shadow-sm"},
                                html.div(
                                    {"class": "flex items-center justify-between"},
                                    html.img({"src": "/static/images/Ellipse 23.svg", "class": "ml-[10%] w-3 h-3"}),
                                    html.div(
                                        {"class": "flex flex-col items-center"},
                                        html.h3({"class": "text-lg font-niconne italic mb-0 leading-none"}, "Ingredients"),
                                        html.img({"src": "/static/images/Line 1.svg", "class": "w-18 h-8 -mt-4"}),
                                    ),
                                    html.img({"src": "/static/images/Ellipse 23.svg", "class": "mr-[10%] w-3 h-3"}),
                                ),
                                html.ul(
                                    {"class": "text-sm font-niconne italic m-0 p-0"},
                                    *[html.li({"class": "border-b-1 border-greyline-100 leading-[0.7] mt-2"}, f"- {i}") for i in recipe_detail["ingredients"]],
                                    [html.li({"class": "leading-[0.7] mt-2 border-b border-greyline-100"},"\u00A0") for _ in range(4)],
                                ),
                            ),
                        ),

                        # Image
                        html.div(
                            {"class": "w-1/3 h-1/2 bg-orange-200 flex rounded-lg items-center justify-center text-6xl"},
                            "🍔",
                        ),

                        # Action buttons
                        html.div(
                            {"class": "flex flex-col gap-2"},
                            html.button(
                                {"class": "w-7 h-6 flex items-center justify-center", "title": "Save"},
                                html.img({"src": "/static/images/Bookmark.svg", "alt": "Save", "class": "w-4 h-4"}),
                            ),
                            html.button(
                                {"class": "w-7 h-6 flex items-center justify-center", "title": "Add to shopping list"},
                                html.img({"src": "/static/images/Shopping cart.svg", "alt": "Add to shopping list", "class": "w-4 h-4"}),
                            ),
                            html.button(
                                {"class": "w-7 h-6 flex items-center justify-center", "title": "Favourite"},
                                html.img({"src": "/static/images/heart.svg", "alt": "Favourite", "class": "w-4 h-4"}),
                            ),
                        ),
                    ),

                    # Method
                    html.div(
                        {"class": "mt-6"},
                        html.h3({"class": "text-base font-bold mb-2"}, "Method"),
                        html.ul(
                            {"class": "list-disc list-inside text-sm space-y-2"},
                            *[html.li(step) for step in recipe_detail["method"]],
                        ),
                    ),
                ),

                # Fake scrollbar track
                html.div(
                    {"class": "fake-track my-4 mr-1", "id": "detail-track"},
                    html.div({"class": "fake-thumb", "id": "detail-thumb"}),
                ),
            ),
        ),
        # ================= FOOTER =================
        html.footer(
            {"class": "flex-shrink-0 h-10 flex items-center justify-center bg-beige-50 border-t text-xs text-gray-600"},
            "Privacy · Terms · Advertising · Cookies · More",
        ),

        # +++ ADDED: JS to drive both fake scrollbars +++
        html.script("""
            function initFakeScrollbar(contentId, trackId, thumbId) {
                const content = document.getElementById(contentId);
                const track   = document.getElementById(trackId);
                const thumb   = document.getElementById(thumbId);

                if (!content || !track || !thumb) return;


                function updateThumb() {
                    const trackHeight = track.clientHeight;
                    const ratio       = content.clientHeight / content.scrollHeight;
                    const thumbHeight = thumb.clientHeight;
                    const maxTop      = trackHeight - thumbHeight;
                    const availableTrack = trackHeight - thumbHeight;
                    const scrollProgress = content.scrollTop / (content.scrollHeight - content.clientHeight);
                    const thumbTop       = scrollProgress * availableTrack;


                    thumb.style.top    = thumbTop + 'px';
                }

                function resizeThumb() {
                    const ratio       = content.clientHeight / content.scrollHeight;
                    if (ratio >= 1) {
                        thumb.style.display = 'none';
                    }
                    else {
                        thumb.style.display = 'block';
                        thumb.style.height = ratio * content.clientHeight/2 + 'px';
                    }
                }
                resizeThumb();
                content.addEventListener('scroll', updateThumb);
                window.addEventListener('resize', updateThumb);
                window.addEventListener('resize', resizeThumb);

                // Drag logic
                thumb.addEventListener('mousedown', (e) => {
                    const startY         = e.clientY;
                    const startScrollTop = content.scrollTop;

                    function onDrag(e) {
                        const delta       = e.clientY - startY;
                        const trackHeight = track.clientHeight;
                        const thumbHeight = thumb.clientHeight;
                        const scrollRatio = (content.scrollHeight - content.clientHeight) / (trackHeight - thumbHeight);
                        content.scrollTop = startScrollTop + delta * scrollRatio;
                    }

                    function onUp() {
                        document.removeEventListener('mousemove', onDrag);
                        document.removeEventListener('mouseup', onUp);
                    }

                    document.addEventListener('mousemove', onDrag);
                    document.addEventListener('mouseup', onUp);
                    e.preventDefault();
                });

                // Click on track to jump
                track.addEventListener('click', (e) => {
                    if (e.target === thumb) return;
                    const rect        = track.getBoundingClientRect();
                    const clickY      = e.clientY - rect.top;
                    const ratio       = clickY / track.clientHeight;
                    content.scrollTop = ratio * content.scrollHeight;
                });

                updateThumb();
            }

            // Init after DOM is ready
            setTimeout(() => {
                initFakeScrollbar('grid-scroll',   'grid-track',   'grid-thumb');
                initFakeScrollbar('detail-scroll', 'detail-track', 'detail-thumb');
            }, 100);
        """),
    )
