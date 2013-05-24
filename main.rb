def reload!
	 #Important ruby-level helpers
	 load 'helpers.rb'
    load 'properties.rb'
    load 'noun.rb'
	 load 'forms.rb'

    #The Books of Creation
    load 'books/metaproperties.rb'
    load 'books/biological.rb'
    load 'books/container.rb'
    load 'books/physical.rb'
    load 'books/player.rb'
    load 'books/psychological.rb'

	 load 'books/basic_forms.rb'

    #The Atlas
	 load 'world.rb'

    load 'terminal.rb'

	 include Forms
	 include Properties

   def wait(who=nil)
      $world.tick;
      who.do(:tick, who) unless who.nil?;
   end

   make_world
end
alias :reload :reload!

reload!
