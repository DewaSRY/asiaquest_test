# frontend architecture 

on the frontend part, is contain more pattern then the backend and there also have technical layer need to cover by manual code, which the solution of the problem is invented by my self not from external library 

for the design and reusable component part i am relay on usage of veutify a library component of vue, it's library component with design base on material ui 3, usage of this library make the need of create custom component is lesser. 

then for the code structure, nuxt 4 it's self already has it's own structure. then i will explain how i follow it's structure to cover the business needs: 

```bash 
/app                       # app is container of source code 
    /components            # component is directory of ui/view component
        /form              # component of form (use to collect data and send it to server)
        /page              # component of page, this component use to layout all units to be a full page
        /tabeldata         # component of list data
        /ui                # ui is reusable component 
    /composables           # composable is logic can be reuse across the component 
    /layouts               # layouts is wrapper for the page, it's likely contain of navigation anchor or button who effecting globally 
    /middlewares           # middleware is a logic run before the page load
    /pages                 # pages is directory use to routing the page
    /plugins               # plugins is directory usually used to config the module extend on the nuxt application 
    /shared                # shared is a code can be shared across the component 
/server                    # server is place we can passing data from the browser to send to the server. this directory used when the app is SSR

```