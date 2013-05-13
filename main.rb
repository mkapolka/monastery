def reload!
	 #Important ruby-level helpers
	 load 'helpers.rb'

	 #Properties
   load 'properties.rb'
	 load 'physical.rb'

   load 'noun.rb'
	 load 'templates.rb'
	 load 'biological.rb'

	 load 'world.rb'

	 include Nouns
	 include Properties
end

def wait(who)
	who.do(:tick, who);
end

reload!
