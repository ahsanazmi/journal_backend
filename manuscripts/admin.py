# 📄 manuscripts/admin.py

from django.contrib import admin
from django.db import transaction
from django.utils.html import format_html, escape
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.db.models import Q, Count
from .models import Manuscript, Review, Author
from .emails import send_reviewer_assignment_email, send_acceptance_email, send_final_decision_email, send_status_update_email
from users.models import User


# 🔹 Inline for Authors
class AuthorInline(admin.TabularInline):
    model = Author
    extra = 1
    fields = ('name', 'email', 'mobile', 'is_main_author')
    classes = ['collapse']


# 🔹 Inline for Reviewers & Reviews
class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1
    fields = ('reviewer', 'decision', 'comments', 'review_code')
    readonly_fields = ('review_code',)
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Only show reviewers in reviewer dropdown"""
        if db_field.name == 'reviewer':
            kwargs['queryset'] = User.objects.filter(role='reviewer')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# 🔹 Manuscript Admin - Full Workflow Management
@admin.register(Manuscript)
class ManuscriptAdmin(admin.ModelAdmin):
    list_display = (
        'paper_id_link', 
        'title_short', 
        'status_badge', 
        'decision_badge', 
        'reviewers_count',
        'author_names', 
        'created_at'
    )
    list_filter = ('status', 'final_decision', 'created_at')
    search_fields = ('paper_id', 'title', 'authors__email', 'authors__name')
    readonly_fields = ('paper_id', 'created_at', 'updated_at', 'file_download', 'review_summary')
    ordering = ('-created_at',)
    
    fieldsets = (
        ("📄 Manuscript Info", {
            "fields": ('paper_id', 'title', 'file', 'file_download', 'created_at', 'updated_at')
        }),
        ("📊 Workflow Status", {
            "fields": ('status', 'admin_notes')
        }),
        ("✅ Final Decision", {
            "fields": ('final_decision',)
        }),
        ("📋 Review Summary", {
            "fields": ('review_summary',),
            "classes": ['collapse']
        }),
    )
    
    inlines = [AuthorInline, ReviewInline]
    
    actions = ['send_acceptance_emails', 'mark_under_review', 'mark_rejected', 'mark_accepted', 'mark_revision']

    def save_model(self, request, obj, form, change):
        """Save manuscript and notify the main author when admin changes status."""
        old_status = None
        old_final_decision = None
        if change and obj.pk:
            previous = Manuscript.objects.filter(pk=obj.pk).first()
            if previous:
                old_status = previous.status
                old_final_decision = previous.final_decision

        super().save_model(request, obj, form, change)

        if change and (old_status != obj.status or old_final_decision != obj.final_decision):
            author = obj.authors.filter(is_main_author=True).first()
            if author:
                transaction.on_commit(
                    lambda: send_status_update_email(
                        obj,
                        author.email,
                        old_status=old_status,
                        new_status=obj.status,
                    )
                )

    def paper_id_link(self, obj):
        """Clickable paper ID"""
        return format_html(
            '<strong style="color: #0066cc; font-size: 14px;">{}</strong>',
            obj.paper_id
        )
    paper_id_link.short_description = "Paper ID"

    def title_short(self, obj):
        """Truncated title"""
        title = obj.title[:50]
        if len(obj.title) > 50:
            title += "..."
        return title
    title_short.short_description = "Title"

    def status_badge(self, obj):
        """Color-coded status badge"""
        colors = {
            'submitted': '#9C27B0',
            'under_review': '#2196F3',
            'accepted': '#4CAF50',
            'rejected': '#F44336',
            'revision': '#FF9800',
        }
        color = colors.get(obj.status, '#757575')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = "Status"

    def decision_badge(self, obj):
        """Color-coded decision badge"""
        colors = {
            'pending': '#9E9E9E',
            'accepted': '#4CAF50',
            'rejected': '#F44336',
            'revision': '#FF9800',
        }
        color = colors.get(obj.final_decision, '#757575')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_final_decision_display()
        )
    decision_badge.short_description = "Decision"

    def reviewers_count(self, obj):
        """Show number of assigned reviewers"""
        count = obj.reviews.count()
        if count == 0:
            color = '#F44336'
            text = '⚠️ None'
        elif count < 2:
            color = '#FF9800'
            text = f'⚡ {count}'
        else:
            color = '#4CAF50'
            text = f'✓ {count}'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 8px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            text
        )
    reviewers_count.short_description = "Reviewers"

    def author_names(self, obj):
        """Display author names"""
        authors = obj.authors.all()
        names = [a.name for a in authors]
        return ", ".join(names) if names else "—"
    author_names.short_description = "Authors"

    def file_download(self, obj):
        """Show file download link"""
        if obj.file:
            return format_html(
                '<a href="{}" target="_blank" style="color: #0066cc; '
                'text-decoration: none; font-weight: bold;">📥 Download Manuscript</a>',
                obj.file.url
            )
        return mark_safe('<span style="color: #999;">No file uploaded</span>')
    file_download.short_description = "📎 Manuscript File"

    def review_summary(self, obj):
        """Show review summary"""
        reviews = obj.reviews.all()
        if not reviews:
            return "No reviewers assigned yet"
        
        html = '<table style="border-collapse: collapse; width: 100%;">'
        html += '<tr style="background-color: #f5f5f5; border-bottom: 1px solid #ddd;">'
        html += '<th style="padding: 8px; text-align: left;">Reviewer</th>'
        html += '<th style="padding: 8px; text-align: left;">Decision</th>'
        html += '<th style="padding: 8px; text-align: left;">Code</th>'
        html += '</tr>'
        
        for review in reviews:
            decision_color = {
                'pending': '#9E9E9E',
                'accepted': '#4CAF50',
                'rejected': '#F44336',
            }.get(review.decision, '#757575')
            
            html += f'<tr style="border-bottom: 1px solid #eee;">'
            html += f'<td style="padding: 8px;">{review.reviewer.username}</td>'
            html += f'<td style="padding: 8px;"><span style="background-color: {decision_color}; '
            html += f'color: white; padding: 3px 6px; border-radius: 3px;">{review.get_decision_display()}</span></td>'
            html += f'<td style="padding: 8px; color: #666;">{review.review_code}</td>'
            html += '</tr>'
        
        html += '</table>'
        return mark_safe(html)
    review_summary.short_description = "Review Details"

    def send_acceptance_emails(self, request, queryset):
        """Send acceptance emails to selected papers"""
        count = 0
        for manuscript in queryset.filter(final_decision='accepted'):
            author = manuscript.authors.filter(is_main_author=True).first()
            if author:
                try:
                    send_acceptance_email(manuscript, author.email)
                    count += 1
                except Exception as e:
                    print(f"Email error: {e}")
        
        self.message_user(request, f"✅ {count} acceptance emails sent!")
    send_acceptance_emails.short_description = "📧 Send acceptance emails"

    def mark_under_review(self, request, queryset):
        """Mark papers as under review"""
        updated = 0
        for manuscript in queryset:
            old_status = manuscript.status
            old_final_decision = manuscript.final_decision
            manuscript.status = 'under_review'
            manuscript.save()
            author = manuscript.authors.filter(is_main_author=True).first()
            if author and old_status != manuscript.status:
                send_status_update_email(manuscript, author.email, old_status=old_status, new_status=manuscript.status)
            updated += 1
        self.message_user(request, f"✅ {updated} papers marked as 'Under Review'")
    mark_under_review.short_description = "Mark as Under Review"

    def mark_rejected(self, request, queryset):
        """Mark papers as rejected"""
        updated = 0
        for manuscript in queryset:
            old_status = manuscript.status
            old_final_decision = manuscript.final_decision
            manuscript.status = 'rejected'
            manuscript.final_decision = 'rejected'
            manuscript.save()
            author = manuscript.authors.filter(is_main_author=True).first()
            if author and (old_status != manuscript.status or old_final_decision != manuscript.final_decision):
                send_status_update_email(manuscript, author.email, old_status=old_status, new_status=manuscript.status)
            updated += 1
        self.message_user(request, f"❌ {updated} papers marked as Rejected")
    mark_rejected.short_description = "Mark as Rejected"

    def mark_accepted(self, request, queryset):
        """Mark papers as accepted and notify authors"""
        updated = 0
        for manuscript in queryset:
            old_status = manuscript.status
            old_final_decision = manuscript.final_decision
            manuscript.final_decision = 'accepted'
            manuscript.status = 'accepted'
            manuscript.save()
            author = manuscript.authors.filter(is_main_author=True).first()
            if author and (old_status != manuscript.status or old_final_decision != manuscript.final_decision):
                send_status_update_email(manuscript, author.email, old_status=old_status, new_status=manuscript.status)
            updated += 1
        self.message_user(request, f"✅ {updated} papers marked as accepted")
    mark_accepted.short_description = "Mark as Accepted"

    def mark_revision(self, request, queryset):
        """Mark papers as requiring revision"""
        updated = 0
        for manuscript in queryset:
            old_status = manuscript.status
            old_final_decision = manuscript.final_decision
            manuscript.status = 'revision'
            manuscript.final_decision = 'revision'
            manuscript.save()
            author = manuscript.authors.filter(is_main_author=True).first()
            if author and (old_status != manuscript.status or old_final_decision != manuscript.final_decision):
                send_status_update_email(manuscript, author.email, old_status=old_status, new_status=manuscript.status)
            updated += 1
        self.message_user(request, f"🔁 {updated} papers marked as 'Revision Required'")
    mark_revision.short_description = "Mark as Revision Required"


# 🔹 Review Admin - Track Reviews
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('review_code', 'manuscript_link', 'reviewer_name', 'decision_badge', 'assigned_at')
    list_filter = ('decision', 'assigned_at')
    search_fields = ('manuscript__paper_id', 'reviewer__username', 'review_code')
    readonly_fields = ('review_code', 'assigned_at', 'manuscript_link')
    ordering = ('-assigned_at',)
    
    fieldsets = (
        ("📋 Assignment", {
            "fields": ('manuscript_link', 'reviewer', 'review_code', 'assigned_at')
        }),
        ("✍️ Review", {
            "fields": ('decision', 'comments')
        }),
    )

    def manuscript_link(self, obj):
        """Link to manuscript"""
        url = reverse('admin:manuscripts_manuscript_change', args=[obj.manuscript.id])
        return format_html(
            '<a href="{}">{} - {}</a>',
            url,
            obj.manuscript.paper_id,
            obj.manuscript.title[:40]
        )
    manuscript_link.short_description = "Manuscript"

    def reviewer_name(self, obj):
        """Reviewer name with email"""
        return format_html(
            '{} <br><span style="color: #666; font-size: 12px;">{}</span>',
            obj.reviewer.username,
            obj.reviewer.email
        )
    reviewer_name.short_description = "Reviewer"

    def decision_badge(self, obj):
        """Decision with color"""
        colors = {
            'pending': '#9E9E9E',
            'accepted': '#4CAF50',
            'rejected': '#F44336',
        }
        color = colors.get(obj.decision, '#757575')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_decision_display()
        )
    decision_badge.short_description = "Decision"

    def get_readonly_fields(self, request, obj=None):
        """Make fields readonly when editing existing review"""
        if obj:
            return self.readonly_fields + ['manuscript', 'reviewer']
        return self.readonly_fields


