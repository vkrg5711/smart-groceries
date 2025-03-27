from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import uuid

from .models import GroceryList, GroceryItem
from .utils import upload_image_to_s3


CATALOGUE = [
    {"id": 1, "name": "Apples",    "price": 1.50, "image_url": "https://www.bigbasket.com/media/uploads/p/xxl/10000352-2_13-fresho-apple-shimla.jpg"},
    {"id": 2, "name": "Bananas",   "price": 0.70, "image_url": "https://www.nipponexpress.com/press/report/img/06-Nov-20-1.jpeg"},
    {"id": 3, "name": "Oranges",   "price": 1.20, "image_url": "https://cdn-prod.medicalnewstoday.com/content/images/articles/272/272782/oranges-in-a-box.jpg"},
    {"id": 4, "name": "Milk",      "price": 2.50, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR1pqJcWUlllhzBSxrADCdgmCw0jSwnrgjbhA&s"},
    {"id": 5, "name": "Bread",     "price": 1.80, "image_url": "https://www.allrecipes.com/thmb/CjzJwg2pACUzGODdxJL1BJDRx9Y=/1500x0/filters:no_upscale():max_bytes(150000):strip_icc()/6788-amish-white-bread-DDMFS-4x3-6faa1e552bdb4f6eabdd7791e59b3c84.jpg"},
    {"id": 6, "name": "Eggs",      "price": 3.00, "image_url": "https://static.toiimg.com/thumb/msid-71200465,width-1280,height-720,imgsize-177052,resizemode-6,overlay-toi_sw,pt-32,y_pad-40/photo.jpg"},
    {"id": 7, "name": "Cheese",    "price": 4.00, "image_url": "https://static.toiimg.com/thumb/msid-115029115,width-400,resizemode-4/115029115.jpg"},
    {"id": 8, "name": "Tomatoes",  "price": 0.90, "image_url": "https://www.fervalle.com/wp-content/uploads/2022/07/580b57fcd9996e24bc43c23b-1024x982.png"},
    {"id": 9, "name": "Potatoes",  "price": 0.50, "image_url": "https://www.jiomart.com//images/product/240x240/590003516/potato-1-kg-product-images-o590003516-p590003516-0-202408070949.jpg"},
    {"id": 10, "name": "Onions",   "price": 0.40, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR_c4mzTsqYoLWHNziM4mHQEEp6-qCek6H7bQ&s"},
    {"id": 11, "name": "Carrots",  "price": 0.60, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcT_ToaAW0-o-fBzVFUsefJ0Mn1QDVGEFeKZEA&s"},
    {"id": 12, "name": "Chicken",  "price": 5.00, "image_url": "https://hips.hearstapps.com/hmg-prod/images/roast-chicken-recipe-2-66b231ac9a8fb.jpg"},
    {"id": 13, "name": "Fish",     "price": 6.00, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTE2oz1fMWHrwrS2itizJgh2R0ph3Ce2FL9RA&s"},
    {"id": 14, "name": "Rice",     "price": 2.00, "image_url": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRvJlWgt2pYOKkyJyC87ybiAV56fmylG05JZA&s"},
    {"id": 15, "name": "Pasta",    "price": 1.70, "image_url": "https://www.yummytummyaarthi.com/wp-content/uploads/2022/11/red-sauce-pasta-1.jpg"},
]


@login_required(login_url='/login/')
def dashboard(request):
    # My Lists: lists created by the current user.
    my_lists = GroceryList.objects.filter(owner=request.user)
    for glist in my_lists:
        items = glist.groceryitem_set.all()
        total_price = sum(item.quantity * item.price for item in items)
        glist.total_price = total_price
        glist.items_with_total = [(item, item.quantity * item.price) for item in items]
    
    # Shared Lists: lists shared with the current user.
    shared_lists = GroceryList.objects.filter(shared_with=request.user)
    for glist in shared_lists:
        items = glist.groceryitem_set.all()
        total_price = sum(item.quantity * item.price for item in items)
        glist.total_price = total_price
        glist.items_with_total = [(item, item.quantity * item.price) for item in items]
    
    return render(request, 'dashboard.html', {
        'my_lists': my_lists,
        'shared_lists': shared_lists,
    })

@login_required(login_url='/login/')
def create_list(request):
    if request.method == 'POST':
        list_name = request.POST.get('list_name') or "My New Grocery List"
        new_list = GroceryList(name=list_name, owner=request.user)
        new_list.save()
        for item in CATALOGUE:
            qty = request.POST.get(f'quantity_{item["id"]}')
            try:
                qty = int(qty)
            except (ValueError, TypeError):
                qty = 0
            if qty > 0:
                GroceryItem.objects.create(
                    grocery_list=new_list,
                    name=item['name'],
                    quantity=qty,
                    price=item['price'],
                    image_url=item['image_url']
                )
        return redirect('dashboard')
    else:
        return render(request, 'create_list.html', {'catalogue': CATALOGUE})

@login_required(login_url='/login/')
def view_list(request, list_id):
    try:
        glist = GroceryList.objects.get(id=list_id)
    except GroceryList.DoesNotExist:
        return redirect('dashboard')
    # Check ownership or sharing
    if request.user != glist.owner and not glist.shared_with.filter(id=request.user.id).exists():
        return redirect('dashboard')
    items = glist.groceryitem_set.all()
    list_total = sum(item.quantity * item.price for item in items)
    return render(request, 'grocery_list.html', {'grocery_list': glist, 'items': items, 'list_total': list_total})

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect to the next URL if provided; otherwise, fallback to the dashboard.
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='/login/')
def add_item(request, list_id):
    if request.method == 'POST':
        # Retrieve form values
        name = request.POST.get('name')
        quantity = request.POST.get('quantity', '1')
        price = request.POST.get('price', '0')
        image = request.FILES.get('image')  # uploaded file

        # Convert quantity and price to proper data types
        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            quantity, price = 1, 0.0

        image_url = None
        if image:
            # Upload image to S3 and retrieve the URL (or None on failure)
            image_url = upload_image_to_s3(image)

        if name:
            grocery_list = get_object_or_404(GroceryList, id=list_id)
            item = GroceryItem(
                grocery_list=grocery_list, 
                name=name, 
                quantity=quantity, 
                price=price, 
                image_url=image_url  # Save the S3 URL in the model
            )
            item.save()
    return redirect('view_list', list_id=list_id)

@login_required(login_url='/login/')
def edit_item(request, item_id):
    # Retrieve the item or return 404 if not found.
    item = get_object_or_404(GroceryItem, id=item_id)
    if request.method == 'POST':
        # Retrieve form fields
        name = request.POST.get('name')
        quantity = request.POST.get('quantity', '1')
        price = request.POST.get('price', '0')
        new_image = request.FILES.get('image')  # new image upload, if provided

        # Convert numeric fields
        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            quantity, price = 1, 0.0

        if name:
            item.name = name
            item.quantity = quantity
            item.price = price
            # Check if a new image was supplied; if so, upload and update URL.
            if new_image:
                image_url = upload_image_to_s3(new_image)
                if image_url:
                    item.image_url = image_url
            item.save()
            return redirect('view_list', list_id=item.grocery_list.id)
    return render(request, 'edit_item.html', {'item': item})

@login_required(login_url='/login/')
def edit_list(request, list_id):
    glist = get_object_or_404(GroceryList, id=list_id)
    # Build a dictionary of the current items in the list by name
    existing_items = {item.name: item.quantity for item in glist.groceryitem_set.all()}
    catalog_with_qty = []
    for item in CATALOGUE:
        item_copy = item.copy()  # make a copy so we do not alter the catalogue
        item_copy['quantity'] = existing_items.get(item['name'], 0)
        catalog_with_qty.append(item_copy)
    if request.method == 'POST':
        list_name = request.POST.get('list_name') or glist.name
        glist.name = list_name
        glist.save()
        # Delete all existing items before recreating
        glist.groceryitem_set.all().delete()
        for item in CATALOGUE:
            qty = request.POST.get(f'quantity_{item["id"]}')
            try:
                qty = int(qty)
            except (ValueError, TypeError):
                qty = 0
            if qty > 0:
                GroceryItem.objects.create(
                    grocery_list=glist,
                    name=item['name'],
                    quantity=qty,
                    price=item['price'],
                    image_url=item['image_url']
                )
        return redirect('dashboard')
    else:
        return render(request, 'edit_list.html', {'catalogue': catalog_with_qty, 'grocery_list': glist})

@login_required(login_url='/login/')
def delete_item(request, item_id):
    item = get_object_or_404(GroceryItem, id=item_id)
    grocery_list_id = item.grocery_list.id
    if request.method == 'POST':
        item.delete()
        return redirect('view_list', list_id=grocery_list_id)
    return render(request, 'delete_item.html', {'item': item})


@login_required(login_url='/login/')
def delete_list(request, list_id):
    glist = get_object_or_404(GroceryList, id=list_id)
    if request.method == 'POST':
        glist.delete()
        return redirect('dashboard')
    return render(request, 'delete_list.html', {'grocery_list': glist})

@login_required(login_url='/login/')
def get_share_link(request, list_id):
    # Only allow the list owner to share
    glist = get_object_or_404(GroceryList, id=list_id, owner=request.user)
    if not glist.share_token:
        glist.share_token = uuid.uuid4().hex
        glist.save()
    share_link = request.build_absolute_uri(f"/share/{glist.share_token}/")
    return render(request, "share_link.html", {"share_link": share_link})



def share_list(request, token):
    """
    When a shared link is clicked:
      - If the user is not authenticated, redirect them to the login page with next set to this share URL.
      - Once logged in (or signed up), add the user to the shared_with and then redirect to dashboard.
    """
    try:
        glist = GroceryList.objects.get(share_token=token)
    except GroceryList.DoesNotExist:
        # Optionally display an error if the token is invalid.
        return redirect('login')
    
    if not request.user.is_authenticated:
        # Redirect to login so that after authentication, the user returns to this share URL.
        return redirect(f"/login/?next=/share/{token}/")
    
    # If the current user is not the owner, add them to the shared lists.
    print(glist.owner)
    print(request.user)

    if request.user != glist.owner:
        glist.shared_with.add(request.user)
        glist.save()
    return redirect('dashboard')