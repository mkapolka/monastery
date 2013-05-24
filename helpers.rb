#Here are some helper methods that you may find helpful in your writing

require 'active_support/core_ext/class/attribute.rb'

class Object
   #Get the metaclass / eigenclass
   def metaclass; class << self; self; end; end

end
