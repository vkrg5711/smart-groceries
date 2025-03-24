from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import GroceryList, GroceryItem
from .utils import upload_image_to_s3

@login_required(login_url='/login/')
def dashboard(request):
    lists = GroceryList.objects.filter(owner=request.user)
    for glist in lists:
        items = glist.groceryitem_set.all()
        total_price = sum(item.quantity * item.price for item in items)
        # Attach total price to the list object
        glist.total_price = total_price
        # Create a list of tuples: (item, item_total)
        glist.items_with_total = [(item, item.quantity * item.price) for item in items]
    return render(request, 'dashboard.html', {'grocery_lists': lists})

@login_required(login_url='/login/')
def create_list(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            new_list = GroceryList(name=name, owner=request.user)
            new_list.save()
            return redirect('dashboard')
    return render(request, 'create_list.html')

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
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
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
def delete_item(request, item_id):
    item = get_object_or_404(GroceryItem, id=item_id)
    grocery_list_id = item.grocery_list.id
    if request.method == 'POST':
        item.delete()
        return redirect('view_list', list_id=grocery_list_id)
    return render(request, 'delete_item.html', {'item': item})



