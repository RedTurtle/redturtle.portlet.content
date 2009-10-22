from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.vocabularies.catalog import SearchableTextSourceBinder

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from redturtle.portlet.content import ContentPortletMessageFactory as _


class IContentPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    showTitle = schema.Bool(title=_(u"show_title",default=u"Show title"),
                               description = _(u"Show the title of the object."),
                               required = False)
    
    showDescr = schema.Bool(title=_(u"Show description"),
                               description = _(u"Show the description of the object."),
                               default = False,
                               required = False)
    
    showText = schema.Bool(title=_(u"Show text"),
                               description = _(u"Show the formatted text of the object, if there is."),
                               default = False,
                               required = False)
    
    showImage = schema.Bool(title=_(u"Show image"),
                               description = _(u"Show the image of the object, if there is."),
                               default = False,
                               required = False)
    
    showMore = schema.Bool(title=_(u"Show more"),
                               description = _(u"Is a link to the object, to show all the informations."),
                               required = False)
    
    content = schema.Choice(title=_(u"Target object"),
                            description=_(u"Find the items to show."),
                            required=True,
                            source=SearchableTextSourceBinder({}, default_query='path:'))
    
    portletId = schema.TextLine(title=_(u"Class of the portlet"),
                            description=_(u"Insert a class for the portlet stylesheet. If empty, the class will be the id of the object."),
                            required=False)



class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IContentPortlet)
    
    def __init__(self,showTitle=False,showDescr=False,showText=False,showImage=False,showMore=False,content=None,portletId=''):
        self.showTitle=showTitle
        self.showDescr = showDescr
        self.showText = showText
        self.showImage = showImage
        self.showMore = showMore
        self.content = content
        self.portletId = portletId


    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Generic content portlet"


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('contentportlet.pt')
    
    def getItem(self):
        context = self.context
        root_path= context.portal_url.getPortalObject().getPhysicalPath()
        item_path = self.data.content.split('/')
        item_url= '/'.join(root_path) + '/'.join(item_path[:-1])
        item = context.portal_catalog(path={'query':item_url,'depth':1},id=item_path[-1])
        if item:
            return item[0]
        else:
            return []
        
    def needObj(self,item):
        if self.data.showTitle or self.data.showImage:
            return item.getObject()
        else:
            return False
    
    def getPortletId(self,item):
        if self.data.portletId:
            return self.data.portletId
        else:
            return item.getId

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IContentPortlet)
    form_fields['content'].custom_widget = UberSelectionWidget
    
    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IContentPortlet)
    form_fields['content'].custom_widget = UberSelectionWidget
