from django.shortcuts import render
from .models import Recipe, Ingredient, Season, Geography
from django.db.models import Q
import json
# Detail View serach
def recipe_search(request):
    return render(request, 'recipes/recipe_search.html')


def search_recipes(request):
    query = request.GET.get('query', '')
    id = request.GET.get('searchbarID', '')[-1]
    IdtoColumn = {"1" : "title", "2" : "ingredients", "3" : "season", "4" : "geography"}
    column = IdtoColumn[id]
    results = []
    show = 1 # decides to show results or not
    regex_pattern = rf' {query}\w*'
    if id == '2':
        filter_kwargs = {f"name__istartswith": query}
        if query:
            results = Ingredient.objects.filter(**filter_kwargs)[:20]
            if len(results) < 20:
                # If fewer than 10 results, find more ingredients starting with the query
                remaining_count = 20 - len(results)
                additional_results = Ingredient.objects.filter(name__iregex=regex_pattern).exclude(id__in=[r.id for r in results])[:remaining_count]
                results = list(results) + list(additional_results)
            if len(results) == 0:
                show = 2
        else:
            show = 0
    elif id == '3':
        filter_kwargs = {f"name__istartswith": query}
        if query:
            results = Season.objects.filter(**filter_kwargs)
        else:
            show = 0
    elif id == '4':
        filter_kwargs = {f"name__istartswith": query}
        filter_kwargs_region = {f"region__istartswith": query}
        if query:
            results = Geography.objects.filter(**filter_kwargs)[:10]
            additional_results = list(Geography.objects.filter(**filter_kwargs_region).values_list("region", flat=True).distinct())
            if len(results) < 10:
                remaining_count = 10 - len(additional_results) - len(results)
                additional_results = additional_results + list(Geography.objects.filter(name__iregex=regex_pattern).exclude(id__in=[r.id for r in results])[:remaining_count])
                remaining_count = 10 - len(additional_results) - len(results)
                additional_results = additional_results + list(Geography.objects.filter(sub_region__iregex=regex_pattern).values_list("sub_region", flat=True).distinct()[:remaining_count])
                remaining_count = 10 - len(additional_results) - len(results)
                additional_results = additional_results + list(Geography.objects.filter(intermediate_region__iregex=regex_pattern).values_list("intermediate_region", flat=True).distinct()[:remaining_count])
            results = list(results) + additional_results
            if len(results) == 0:
                show = 2
        else:
            show = 0
    else:
        filter_kwargs = {f"{column}__istartswith": query}
        iregex_kwargs = {f"{column}__iregex": regex_pattern}
        if query:
            results = Recipe.objects.filter(**filter_kwargs)[:20]
            if len(results) < 20:
                # If fewer than 10 results, find more recipes starting with the query
                remaining_count = 20 - len(results)
                additional_results = Recipe.objects.filter(**iregex_kwargs).exclude(id__in=[r.id for r in results])[:remaining_count]
                results = list(results) + list(additional_results)
            if len(results) == 0:
                show = 2
        else:
            show = 0
    # Render a partial HTML template with search results
    return render(request, 'partials/search_results.html', {'results': results, 'type': column, "show": show})

def recipe_list(request):
    recipe = json.loads(request.GET.get('tag', ''))
    variables= {
        'title': recipe["title"],
        'season': recipe["season"],
        'geography': recipe["geography"]
    }
    return render(request, 'partials/recipes.html', variables)

def ingredient_list(request):
    ingredients = json.loads(request.GET.get('tag', ''))
    variables= {
        'ingredients': ingredients,
    }
    return render(request, 'partials/ingredients.html', variables)


def get_filter_kwargs(title_list, season_list, geography_list, ingredient_list):
    filters = Q()

    if title_list:
        filters |= Q(title__in=title_list)

    if season_list:
        for season in season_list:
            filters |= Q(season__icontains=season)

    if geography_list:
        for geography in geography_list:
            filters |= Q(geography__icontains=geography)

    if ingredient_list:
        for ingredient in ingredient_list:
            filters &= Q(ingredients__contains=f'"ingrediant_key": "{ingredient.lower()}"')

    return filters

def recipe_button_list(request):
    results = json.loads(request.GET.get('tag', ''))
    if all(len(value) == 0 for value in results.values()):
        recipes = Recipe.objects.order_by("?")
    else:
        if "autumn" in results["season"]:
            results["season"].append("fall")
        filter_kwargs = get_filter_kwargs(results["title"], results["season"], results["geography"], results["ingredients"])
        recipes = Recipe.objects.filter(filter_kwargs).distinct()
    variables= {
        'recipes': recipes,
    }
    return render(request, 'partials/recipe_buttons.html', variables)


def recipe_display(request):
    recipe = json.loads(request.GET.get('recipe', ''))
    ingredients = json.loads(recipe["ingredients"])
    for ingredient in ingredients:
        for key, value in ingredient.items():
            if value is None:
                ingredient[key] = ""
            elif key == "amount":
                ingredient[key] = "{:g}".format(value)
    variables= {
        'title': recipe["title"],
        'ingredients': ingredients,
        'directions': recipe["directions"],
        'total_yield': recipe["total_yield"]
    }
    return render(request, 'partials/recipe-display.html', variables)

