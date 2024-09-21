from django.shortcuts import render, redirect,HttpResponse

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

from django.template import loader
from django.views import View
from django.shortcuts import get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from group.models import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import pandas as pd

# from django.template import loader
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.contrib.auth.decorators import login_required
# from django.urls import reverse_lazy


class Index(View):
    def get(self,request):
        alert_title = request.session.get('alert_title',False)
        alert_detail = request.session.get('alert_detail',False)
        if(alert_title):del(request.session['alert_title'])
        if(alert_detail):del(request.session['alert_detail'])
        context = {
            'alert_title': alert_title,
            'alert_detail': alert_detail,
            "page_name":"Home"
        }
        try:
            if request.user.is_anonymous:
                return redirect("/login")
            elif not request.user.is_staff and not request.user.is_superuser:
                return render(request,"student_index.html",context)
            elif not request.user.is_superuser and request.user.is_staff:
                return render (request,"teacher_index.html",context)
            else :
                request.session['alert_title'] = "Invalid Access Attempt"
                request.session['alert_detail'] = "User is not Granted Acess."
                return redirect("/login")
        except Exception as e:
            pass
            
class Logout_view(View):
    def get(self,request):
        request.session.clear()
        logout(request)
        return redirect('/')
      
class Login_view(View):
    def get(self,request):
        alert_title = request.session.get('alert_title',False)
        alert_detail = request.session.get('alert_detail',False)
        if(alert_title):del(request.session['alert_title'])
        if(alert_detail):del(request.session['alert_detail'])
        context = {
            'alert_title': alert_title,
            'alert_detail': alert_detail,
            'page_name': 'login'
        }
        return render(request,"signin.html",context)
    
    def post(self,request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        try:
            user = authenticate(username = username, password = password)
            if user is not None:# checks if the user is logged in or not?
                login(request,user) #logins the user
                return redirect ('/')
            else:
                request.session['alert_title'] = "Invalid Login Attempt"
                request.session['alert_detail'] = "Please enter valid login credential."
                return redirect(request.path)
        except Exception as e:
            request.session['alert_title'] = "Invalid Login Attempt"
            request.session['alert_detail'] = "Please enter valid login credential."
            return redirect(request.path)

        
        
class Signup_View (View):
    def get(self,request):
        alert_title = request.session.get('alert_title',False)
        alert_detail = request.session.get('alert_detail',False)
        if(alert_title):del(request.session['alert_title'])
        if(alert_detail):del(request.session['alert_detail'])
        context = {
            'alert_title':alert_title,
            'alert_detail':alert_detail,
            'page_name': 'Signup'
        }
        return render(request,"signup.html",context)
        
    def post(self,request):
        if request.method == 'POST':
            firstName = request.POST.get('firstName')
            lastName = request.POST.get('lastName')
            username = request.POST.get('username')  

            email = request.POST.get('email')
            password = request.POST.get('password')
            status  = request.POST.get('staff')

            # Email Validation
            try:
                validator = EmailValidator()
                validator(email)
            except ValidationError as e:
                request.session['alert_title'] = "Invalid Email"
                request.session['alert_detail'] = "Please enter valid email."
                return redirect(request.path)

            # Determine user type
            is_superuser = False
            is_staff = False
            if status == 'admin':
                is_superuser = True
                is_staff = True
            elif status == 'teacher':
                is_superuser = False
                is_staff = True
            elif status == 'student':
                is_superuser = False
                is_staff = False
                
            try:# Create user with validation
                user = User.objects.create_user(username, email, password, is_superuser=is_superuser, is_staff=is_staff)
                user.first_name = firstName
                user.last_name = lastName
                user.save()
            except Exception as e:
                request.session['alert_title'] = "Registration Fail"
                request.session['alert_detail'] = e
                return redirect(request.path)
                
            try:# Authenticate and Login
                user = authenticate(username=username, password=password)
                if user is not None:# checks if the user is logged in or not?
                    login(request,user) #logins the user
                    return redirect ('/')
                else:
                    # Handle failed authentication (e.g., display error message)
                    request.session['alert_title'] = "Login Fail"
                    request.session['alert_detail'] = "Invalid Attempt to login"
                    return redirect(request.path)
            except Exception as e:
                request.session['alert_title'] = "Registration Fail"
                request.session['alert_detail'] = e
                return redirect(request.path)
        return render(request, "signup.html")



class teacher_form_view(View):
    def get(self,request):
        context = {
            'page-name':'teacher-form'
        }
        return render(request,"teacher-form.html",context)
    def post(self,request):
        if request.method == 'POST':
            user_id = request.user.id
            title = request.POST.get('project-title')
            description = request.POST.get('project-description')

            communication = request.POST.get('communication') is not None
            presentation = request.POST.get('presentation') is not None
            coding = request.POST.get('coding') is not None
            leadership = request.POST.get('leadership') is not None
            form_detail = FormDetail.objects.create(
                user_id = user_id,
                title = title,
                description = description,
                communication=communication,
                presentation = presentation,
                coding = coding,
                leadership = leadership,
            ).save() 
        
        return redirect ('/')  
    
class StudentFormListing(View):
    def get(self, request):
        alert_title = request.session.get('alert_title', False)
        alert_detail = request.session.get('alert_detail', False)
        if alert_title:
            del request.session['alert_title']
        if alert_detail:
            del request.session['alert_detail']
        form_id = FormDetail.objects.all()
        context = {
            'alert_title': alert_title,
            'alert_detail': alert_detail,
            'page_name': 'student form',
            'form_id': form_id
        }
        return render(request, "formlisting.html", context)
        
    def post(self,request):
        pass

class formdetailview(View):
    def get(self, request, title):
        formsingle = get_object_or_404(FormDetail, title=title)
        template = loader.get_template('student-form.html')
        context = {
            'formsingle': formsingle,
        }
        return HttpResponse(template.render(context, request))

    def post(self,request):
        if request.method == 'POST':
            user_id = request.user.id
            title = request.POST.get('form_id')
            communication = request.POST.get('communication')
            presentation = request.POST.get('presentation')
            coding = request.POST.get('coding')
            leadership = request.POST.get('leadership')
            try:
                student_detail = Skillset.objects.create(
                    user_id=user_id,
                    title=title,
                    communication=communication,
                    presentation=presentation,
                    coding=coding,
                    leadership=leadership,
                ).save()
                if student_detail:
                    df = pd.DataFrame.from_dict([student_detail.as_dict()])
                    name = f"{title}.csv"
                    df.to_csv(f"Data/{name}", index=False)
                    return redirect('/')
            except Exception as e:
                print(e)
        return redirect ('/')  


    
    

class student_form_view(View):
    def get(self,request):
        alert_title = request.session.get('alert_title',False)
        alert_detail = request.session.get('alert_detail',False)
        if(alert_title):del(request.session['alert_title'])
        if(alert_detail):del(request.session['alert_detail'])
        form_id = FormDetail.request.object()
        context = {
            'alert_title':alert_title,
            'alert_detail':alert_detail,
            'page_name': 'student form',
            'form_id': form_id
        }
        return render(request,"student-form.html",context)
        
    def post(self,request):
        if request.method == 'POST':
            filename = request.POST.get('filename')
            user_id = request.user.id
            communication = request.POST.get('communication')
            presentation = request.POST.get('presentation')
            coding = request.POST.get('coding')
            leadership = request.POST.get('leadership')
            skillsets = Skillset.objects.create(
                user_id = user_id,
                coding = coding,
                leadership = leadership,
                communication=communication,
                presentation = presentation,
            ).save()  
            df = pd.DataFrame.from_dict(skillsets)
            filename = ''.csv
            df.to_csv(filename, index=False)
        return redirect ('/')  

class Student_Profile_view(View):
    def get(self,request):
        user_id = request.user.id
        context = {
            'user_id': user_id,
        }
        return render(request,"student-profile.html",context)

class Team_generator(View):
    def post(self,request):  # Assuming the form ID is passed in the URL
        if request.method == 'POST':
            form_id = request.POST.get('username')
            context = {}
            # try:
            #     skillset = Skillset.objects.get(form_detail = form_id)
            #     context = {
            #         'detail' = skillset,
            #     }
            return render(request, "team-generator.html", context)

        # Retrieve all users with the same form ID (replace with your logic for getting form_id)
        # users_with_same_form = FormDetail.objects.filter(pk=form_id).values_list('user')  # Optimized query

        # if users_with_same_form:
        #     user_skillsets = []  # List to store extracted data
        #     for user_id in users_with_same_form:
        #         try:
        #             skillset = Skillset.objects.get(user=user_id[0], form_detail=form_id)  # Filter by both user and form ID
        #             user_skillsets.append({
        #                 'user_id': user_id[0],
        #                 'coding': skillset.coding,
        #                 'leadership': skillset.leadership,
        #                 'communication': skillset.communication,
        #                 'presentation': skillset.presentation,
        #             })
        #         except Skillset.DoesNotExist:
        #             pass  # Handle case where a user doesn't have a Skillset object for this form

        #     context['user_skillsets'] = user_skillsets
        # else:
        #     context['message'] = 'No users found with this form ID.'  # Informational message

        
    # def get(self,request):
    #     formDetail_id = 00
    #     if Skillset.objects.filter(id = formDetail_id)
    #     skillset_form_id = 

    #     return render(request,"team-generator.html",context)
# login and sign up related views


'''

form_id1 = FormDetail.object.id
        form_id2 = Skillset.object.id
        if(form_id1 == form_id2):
            coding = Skillset.objects.coding.all
            leadership = Skillset.objects.coding.all
            communication = Skillset.objects.coding.all
            presentation = Skillset.objects.coding.all
            context = {
                'user_id': user_id,
            }

    user_id = request.user.id if request.user.is_authenticated else None

        # Retrieve specific Skillset (replace with your logic)
        skillset_id = request.GET.get('skillset_id')  # Assuming skillset ID is passed in the URL or form
        try:
            skillset = Skillset.objects.get(pk=skillset_id)
            coding = skillset.coding
            leadership = skillset.leadership
            communication = skillset.communication
            presentation = skillset.presentation
        except Skillset.DoesNotExist:
            # Handle case where skillset with ID is not found
            skillset = None
            coding = None  # Set appropriate values for not found case
            leadership = None
            communication = None
            presentation = None

        context = {
            'user_id': user_id,
            'skillset': skillset,  # Pass the entire Skillset object if needed
            'coding': coding,
            'leadership': leadership,
            'communication': communication,
            'presentation': presentation,
        }

'''